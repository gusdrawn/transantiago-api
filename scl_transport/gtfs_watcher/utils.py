import mechanize
import re


class LinkExtractor(object):
    """
    Helper to extract
    """
    _link = None
    _response = None
    _br = None

    def __init__(self, url, contains_text=None, contains_url=None):
        self.url = url
        self.contains_text = contains_text
        self.contains_url = contains_url

    @property
    def br(self):
        if not self._br:
            br = mechanize.Browser()
            br.set_handle_robots(False)
            br.set_handle_refresh(False)
            br.addheaders = [('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
            self._br = br
        return self._br

    @property
    def response(self):
        if not self._response:
            response = self.br.open(self.url, timeout=float(15.0))
            self._response = response
        return self._response

    @property
    def link(self):
        if not self._link:
            assert self.response.code < 400
            if self.contains_text:
                links = self.br.links(text_regex=re.compile(self.contains_text))
            elif self.contains_url:
                links = self.br.links(url_regex=re.compile(self.contains_url))
            count = 0
            for link_obj in links:
                assert count <= 1
                self._link = link_obj.absolute_url
                count += 1
        return self._link
