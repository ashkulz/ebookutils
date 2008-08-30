#!/usr/bin/env python

##
##  Copyright (c) 2008 by the people mentioned in the file AUTHORS.
##
##  This software is licensed under the terms mentioned in the file LICENSE.
##

import sys, getopt, impserve

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

    impserve.run(host, port, args)
    sys.exit(0)

if __name__ == '__main__':
    main(sys.argv[1:])
