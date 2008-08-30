#!/usr/bin/env python

##
##  Copyright (c) 2008 by the people mentioned in the file AUTHORS.
##
##  This software is licensed under the terms mentioned in the file LICENSE.
##

from version import __version__

import os, sys, signal, socket, select, urlparse, urllib, shutil, getopt
import SocketServer, BaseHTTPServer, mimetypes

from   os.path import *

################################################################ service URLs

LOCAL_DOMAIN    = ".ebooksystem.net"
BOOKLIST_PREFIX = "http://bookshelf.ebooksystem.net/bookshelf/default.asp?"
BOOK_PREFIX     = "http://bookshelf.ebooksystem.net/bookshelf/getbook?"
CONTENT_PREFIX  = "http://bookshelf.ebooksystem.net/content/"

LOCAL_MESSAGE   = """
<html><body><h1>Welcome to impserve %s</h1>
<p>Your <a underline='yes' href="%sSHOW_HIDDEN=NO">online bookshelf</a>.</p>
<p>Your <a underline='yes' href="%s">local content</a>.</p>
</body></html>""" % (__version__, BOOKLIST_PREFIX, CONTENT_PREFIX)

INDEX_FILES     = ['index.htm', 'index.html']

############################################################## ebook metadata

def get_ebook_info(name):
    """ get the details of the IMP book as a tuple """
    if not isfile(name):
        return None
    info = [name, getsize(name), getmtime(name)]
    f = open(name, 'rb')
    if f.read(10) != '\x00\x02BOOKDOUG':
        return None

    def cString(skip=0):
        result = ''
        while 1:
            data = f.read(1)
            if data == '\x00':
                if not skip: return result
                skip -= 1
                result, data = '', ''
            result += data

    f.read(38)
    info += [cString(), cString(), cString(1), cString(2)]
    f.close()
    return tuple(info)

def get_ebook_list(path, existing={}):
    """ get the list of ebooks under a given path (with optional caching) """

    if not isdir(path):
        return existing

    current = {}
    for file, info in existing.items():
        if not isfile(file):
            continue
        if getmtime(file) != info[2]:
            current[file] = get_ebook_info(file)
        else:
            current[file] = info

    for root, dirs, files in os.walk(abspath(path)):
        for name in files:
            if name.lower().endswith('.imp'):
                fname = join(root, name)
                if fname not in existing:
                    current[fname] = get_ebook_info(fname)
    return current

################################################################ misc helpers

def get_root():
    """ return the root directory to serve from """

    if 'IMPSERVE_PATH' in os.environ:
        return abspath(os.environ['IMPSERVE_PATH'])
    if isdir(expanduser("~/.impserve")):
        return abspath(expanduser("~/.impserve"))
    if sys.platform == 'win32' and \
            isdir(join(os.environ.get("APPDATA", ""), "impserve")):
        return abspath(expanduser("~/.impserve"))
    if '__file__' in globals():
        return dirname(abspath(__file__))
    if sys.argv[0]:
        return dirname(abspath(sys.argv[0]))
    return abspath(os.getcwd())

class ImpURLopener(urllib.URLopener):
    version = 'impserve/' + __version__
    
    def http_error_default(self, url, fp, errcode, errmsg, headers):
        """Default error handling -- don't raise an exception."""
        return addinfourl(fp, headers, "http:" + url)

urllib._urlopener = ImpURLopener()

###################################################################### server

class ImpProxyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """ the actual HTTP handler class """

    server_version = 'impserve/' + __version__
    root_dir       = get_root()
    shelf_dirs     = [ root_dir ]
    book_cache     = {}

    ############################################################ HTTP handler

    def do_GET(self):
        """Serve a GET request."""

        (proto, host, path, param, qry, frag) = urlparse.urlparse(self.path)

        if proto != 'http' or not host:
            self.send_error(400, 'bad url %s' % self.path)
            return

        if host.lower().endswith(LOCAL_DOMAIN):
            self.handle_local_request(host, path, qry)
            return

        self.handle_proxy_request()

    def do_POST(self):
        """Serve a POST request."""

        (proto, host, path, param, qry, frag) = urlparse.urlparse(self.path)
        if proto != 'http' or not host:
            self.send_error(400, 'bad url %s' % self.path)
            return

        self.handle_proxy_request()

    ############################################################## HTTP proxy

    ## This part is taken from HTTP Debugging Proxy by Xavier Defrang
    ## which in turn was based on TinyHTTPProxy by UZUKI Hisao.

    def handle_proxy_request(self):
        (proto, host, path, param, qry, frag) = urlparse.urlparse(self.path)

        ### FIXME: this is a hack, otherwise query parameters don't work
        ### via the inbuilt browser. Need to investigate it further.

        qry = qry.replace('&amp;', '&')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            try:
                i = host.find(':')
                if i >= 0:
                    host, port = host[:i], int(host[i+1:])
                else:
                    port = 80
                sock.settimeout(10)
                sock.connect((host, port))
            except socket.timeout:
                self.send_error(504, "Proxy has timed out")
                return
            self.log_request()
            str = '%s %s %s\r\n' % (
                self.command,
                urlparse.urlunparse(('', '', path, param, qry, frag)),
                self.request_version)
            sock.send(str)
            self.headers['Connection'] = 'close'
            del self.headers['Proxy-Connection']
            for (h, v) in self.headers.items():
                str = '%s: %s\r\n' % (h, v)
                sock.send(str)
            sock.send('\r\n')
            self.proxy_sendrecv(sock)
        finally:
            sock.close()
            self.connection.close()

    def proxy_sendrecv(self, sock, max_idling=20):
        rfile = self.rfile
        if hasattr(rfile, '_rbuf'):	 # on BeOS?
            data = rfile._rbuf
        else:
            if self.headers.has_key('Content-Length'):
                n = int(self.headers['Content-Length'])
                data = rfile.read(n)
            else:
                self.connection.setblocking(0)
                try: data = rfile.read()
                except IOError: data = ''
                self.connection.setblocking(1)
        rfile.close()
        if data:
            sock.send(data)
        iw = [self.connection, sock]
        count = 0
        while 1:
            count += 1
            (ins, _, exs) = select.select(iw, [], iw, 3)
            if exs: break
            if ins:
                for i in ins:
                    if i is sock:
                        out = self.connection
                    else:
                        out = sock
                    data = i.recv(8192)
                    if data:
                        out.send(data)
                        count = 0
            if count == max_idling: break

    ########################################################### local content

    def handle_local_request(self, host, path, qry):
        if self.path.startswith(BOOKLIST_PREFIX):
            self.reload_cache()
            data = self.get_booklist()
            self.send_response(200)
            self.send_header("Content-Length", len(data))
            self.send_header("Content-type", 'text/x-booklist')
            self.end_headers()
            self.wfile.write(data)
        elif self.path.startswith(BOOK_PREFIX):
            book_id = self.path[len(BOOK_PREFIX):]
            self.reload_cache()
            for info in self.book_cache.values():
                if info[3] == book_id:
                    data = open(info[0], 'rb')
                    self.send_response(200)
                    self.send_header("Content-Length", info[1])
                    self.send_header("Content-type", 'application/x-softbook')
                    self.end_headers()
                    shutil.copyfileobj(data, self.wfile)
                    data.close()
            else:
                self.send_error(404, "File not found")
                return
        elif self.path.startswith(CONTENT_PREFIX):
            loc = join(self.root_dir, normpath(path)[1:])
            if isdir(loc):
                for index in INDEX_FILES:
                    if isfile(join(loc, index)):
                        loc = join(loc, index)
                        break
                else:
                    self.send_error(404, "File not found")
                    return
            elif not isfile(loc):
                    self.send_error(404, "File not found")
                    return
            type = mimetypes.guess_type(loc)[0] or 'application/octet-stream'
            self.send_response(200)
            self.send_header("Content-type", type)
            self.send_header("Content-Length", getsize(loc))
            self.end_headers()
            shutil.copyfileobj(open(loc, 'rb'), self.wfile)
        else:
            self.send_response(200)
            self.send_header("Content-Length", len(LOCAL_MESSAGE ))
            self.send_header("Content-type", 'text/html')
            self.end_headers()
            self.wfile.write(LOCAL_MESSAGE)

    ######################################################## booklist helpers

    def get_booklist(self, start=0, length=9999):
        """ return the updated book list """

        names = self.book_cache.keys()
        names.sort()

        result = "1\r\n"
        for book in names[start:start+length]:
            i = self.book_cache[book]
            result += "None:%s\t%s\t%s\t%s\t%d\t%s\t1\t17\r\n" % \
                      (i[3], i[5], i[6], i[4], i[1], BOOK_PREFIX+i[3])
        result += "\r\n\r\n"
        return result

    def reload_cache(self):
        for dir in self.shelf_dirs:
            self.book_cache = get_ebook_list(dir, self.book_cache)
            
    def address_string(self):
        print self.client_address
        return self.client_address[0]

class ThreadingHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    pass

######################################################################## main

def run(host, port, dirs=[]):
    if not mimetypes.inited:
        mimetypes.init(join(ImpProxyHandler.root_dir, 'mime.types'))
    mimetypes.add_type('application/x-softbook', '.imp')

    for dir in dirs:
        if isdir(dir):
            ImpProxyHandler.shelf_dirs.append(abspath(dir))

    httpd = ThreadingHTTPServer((host,port), ImpProxyHandler)

    sname = httpd.socket.getsockname()
    print "impmake %s: starting server on %s:%s" % \
            (__version__, sname[0], sname[1])

    httpd.serve_forever()

def usage():
    print """
Usage: impserve [-OPTIONS] SHELF-DIRECTORIES
-h          show this help message.
-v          show the version.
-a ADDRESS  listen on the specified IP address (default: 0.0.0.0)
-p PORT     listen on the specified port       (default: 9090)
"""


def main(argv):
    host, port = '', 9090
    try:
        opts, args = getopt.getopt(argv, "hva:p:")
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)
    for o, a in opts:
        if o == '-h':
            usage()
            sys.exit(0)
        elif o == '-v':
            print 'impserve %s' % __version__
            sys.exit(0)
        elif o == '-a':
            host = a
        elif o == '-p':
            port = int(a)
        else:
            print 'Unhandled option'
            sys.exit(3)

    run(host, port, args)
    sys.exit(0)

if __name__ == '__main__':
    main(sys.argv[1:])

