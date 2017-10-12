import arrow


class UTF8Recoder(object):
    """Iterator that reads an encoded stream and encodes the input to UTF-8"""
    def __init__(self, f, encoding):
        import codecs
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode('utf-8')


def convert_str_to_time(time_str):
    input_date = '{} {}'.format('2017/01/01', time_str)
    return arrow.get(input_date, 'YYYY/MM/DD HH:mm:ss').time()
