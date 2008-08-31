import urlparse
import impserve

## hack to get the query parameters working via the inbuilt browser
class AdjustQueryString(impserve.ProxyClient):
    def get_url(self, url):
        (proto, host, path, param, qry, frag) = urlparse.urlparse(url)
        qry = qry.replace('&amp;', '&')
        return urlparse.urlunparse((proto, host, path, param, qry, frag))

