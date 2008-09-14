from ebookutils import impserve
from BeautifulSoup import BeautifulSoup

class AdjustHtml(impserve.ProxyResponse):
    def get_response(self, url, headers, data):
        if not 'text/html' in headers['Content-Type']:
            return headers, data

        soup = BeautifulSoup(data)

        # add the UNDERLINE=YES attribute
        for a in soup.findAll('a', href=True):
            a['UNDERLINE'] = 'YES'

        # remove all <a> tags without a href
        for a in soup.findAll('a', href=None):
            a.extract()

        return headers, soup.renderContents()

