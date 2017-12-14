import mechanize
import re
import StringIO
import requests
import xlrd
import csv


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


def float_to_str(val):
    print "converting", val
    return unicode(int(val))


def str_to_utf8(val):
    return unicode(val).encode('utf-8')


class BIPFeedBase(object):

    xls_file = "tmp.xlsx"
    _link = None
    url = None
    sheet_name = None
    FIELD_MAPPING = []

    def link(self):
        if not self._link:
            link_extractor = LinkExtractor(url=self.url, contains_url=".xlsx")
            self._link = link_extractor.link
        return self._link

    def preprocess_fields(self, input_fields):
        return input_fields

    def get_fields(self, input_fields):
        fields = []
        for idx, field in enumerate(input_fields):
            field_name, converter = self.FIELD_MAPPING[idx]
            if converter:
                fields.append(converter(field))
        return fields

    def write(self):
        # 1: get xlsx link
        link_extractor = LinkExtractor(url=self.url, contains_url=".xlsx")
        u = requests.get(link_extractor.link)
        f = StringIO.StringIO()
        # 2: save xlsx file
        with open(self.xls_file, "wb") as f:
            f.write(u.content)
        f.close()
        # 3: format and write results
        wb = xlrd.open_workbook(self.xls_file)
        sh = wb.sheet_by_name(self.sheet_name)
        shared_csv = open('bip_spots.csv', 'a')
        wr = csv.writer(shared_csv, quoting=csv.QUOTE_ALL)
        for rownum in xrange(sh.nrows):
            try:
                data = sh.row_values(rownum)
                data = self.preprocess_fields(data)
                gt = self.get_fields(data)
                print gt
                wr.writerow(gt)
            except Exception, e:
                print str(e)
                pass

        shared_csv.close()


class RetailBIPFeed(BIPFeedBase):
    url = 'http://datos.gob.cl/dataset/33353'
    sheet_name = 'RETAIL'
    FIELD_MAPPING = [
        ('bip_spot_code', float_to_str),
        ('bip_spot_entity', str_to_utf8),
        ('bip_spot_fantasy_name', str_to_utf8),
        ('bip_spot_address', str_to_utf8),
        ('bip_spot_commune', str_to_utf8),
        ('bip_opening_time', str_to_utf8),
        ('bip_spot_east_ref', float_to_str),
        ('bip_spot_north_ref', float_to_str),
        ('bip_spot_lon', str_to_utf8),
        ('bip_spot_lat', str_to_utf8)
    ]


class MetroBIPFeed1(BIPFeedBase):
    url = 'http://datos.gob.cl/dataset/33355'
    sheet_name = 'Hoja1'
    FIELD_MAPPING = [
        ('bip_spot_code', str_to_utf8),
        ('bip_spot_entity', str_to_utf8),
        ('bip_spot_fantasy_name', str_to_utf8),
        ('bip_spot_address', str_to_utf8),
        ('bip_spot_commune', str_to_utf8),
        ('bip_opening_time', str_to_utf8),
        ('bip_spot_east_ref', float_to_str),
        ('bip_spot_north_ref', float_to_str),
        ('bip_spot_lon', str_to_utf8),
        ('bip_spot_lat', str_to_utf8)
    ]


class MetroBIPFeed2(BIPFeedBase):
    url = 'http://datos.gob.cl/dataset/33355'
    sheet_name = 'METRO'
    FIELD_MAPPING = [
        ('', None),
        ('bip_spot_code', str_to_utf8),
        ('bip_spot_entity', str_to_utf8),
        ('bip_spot_fantasy_name', str_to_utf8),
        ('bip_spot_address', str_to_utf8),
        ('bip_spot_commune', str_to_utf8),
        ('bip_opening_time', str_to_utf8),
        ('bip_spot_east_ref', float_to_str),
        ('bip_spot_north_ref', float_to_str),
        ('bip_spot_lon', str_to_utf8),
        ('bip_spot_lat', str_to_utf8)
    ]


class HighStandardBIPFeed(BIPFeedBase):
    url = 'http://datos.gob.cl/dataset/28192'
    sheet_name = 'PCMAV ALTO ESTANDAR'
    FIELD_MAPPING = [
        ('', None),
        ('bip_spot_code', float_to_str),
        ('bip_spot_entity', str_to_utf8),
        ('bip_spot_fantasy_name', str_to_utf8),
        ('bip_spot_address', str_to_utf8),
        ('bip_spot_commune', str_to_utf8),
        ('bip_opening_time', str_to_utf8),
        ('bip_spot_east_ref', float_to_str),
        ('bip_spot_north_ref', float_to_str),
        ('bip_spot_lon', str_to_utf8),
        ('bip_spot_lat', str_to_utf8)
    ]

    def preprocess_fields(self, input_fields):
        input_fields.insert(3, input_fields[2])
        return input_fields


class NormalStandardBIPFeed(BIPFeedBase):
    url = 'http://datos.gob.cl/dataset/28194'
    sheet_name = 'PCMAV ESTANDAR NORMAL'
    FIELD_MAPPING = [
        ('', None),
        ('bip_spot_code', str_to_utf8),
        ('bip_spot_entity', str_to_utf8),
        ('bip_spot_fantasy_name', str_to_utf8),
        ('bip_spot_address', str_to_utf8),
        ('bip_spot_commune', str_to_utf8),
        ('bip_opening_time', str_to_utf8),
        ('bip_spot_east_ref', float_to_str),
        ('bip_spot_north_ref', float_to_str),
        ('bip_spot_lon', str_to_utf8),
        ('bip_spot_lat', str_to_utf8)
    ]

    def preprocess_fields(self, input_fields):
        input_fields.insert(3, input_fields[2])
        return input_fields
