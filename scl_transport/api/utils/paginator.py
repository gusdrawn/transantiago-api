from math import ceil
from sqlalchemy import func


class InvalidPage(Exception):
    pass


class PageNotAnInteger(InvalidPage):
    pass


class EmptyPage(InvalidPage):
    pass


class Paginator(object):

    def __init__(self, query_set, per_page_limit, optional_count_query_set=None,
                 allow_empty_first_page=True):

        self.query_set = query_set
        self.per_page_limit = per_page_limit
        self.optional_count_query_set = optional_count_query_set
        self.allow_empty_first_page = allow_empty_first_page
        self.__total_pages = self.__count = None
        self.__iter_page = 1

    def __iter__(self):
        self.__iter_page = 1
        return self

    def next(self):

        if self.__iter_page > self.total_pages:
            raise StopIteration
        page = self.page(self.__iter_page)
        self.__iter_page += 1
        return page

    def validate_page_number(self, page_number):

        try:
            page_number = int(page_number)
        except ValueError:
            raise PageNotAnInteger('That page number is not an integer')
        if page_number < 1:
            raise EmptyPage('That page number is less than 1')
        if page_number > self.total_pages:
            if page_number == 1 and self.allow_empty_first_page:
                pass
            else:
                raise EmptyPage('That page contains no results')
        return page_number

    def page(self, page_number):
        page_number = self.validate_page_number(page_number)
        offset = (page_number - 1) * self.per_page_limit
        return Page(self.query_set.offset(offset).limit(self.per_page_limit).all(),
                    page_number, self)

    def __get_count(self):
        if self.__count is None:
            if self.optional_count_query_set is None:
                self.optional_count_query_set = self.query_set.order_by(None)
            count_query = self.optional_count_query_set.statement.with_only_columns([func.count()])
            self.__count = self.optional_count_query_set.session.execute(count_query).scalar()
        return self.__count
    count = property(__get_count)

    def __get_total_pages(self):
        if self.__total_pages is None:
            if self.count == 0 and not self.allow_empty_first_page:
                self.__total_pages = 0
            else:
                hits = max(1, self.count)
                self.__total_pages = int(ceil(hits / float(self.per_page_limit)))
        return self.__total_pages
    total_pages = property(__get_total_pages)

    def __pages_range(self):
        return range(1, self.total_pages + 1)
    pages_range = property(__pages_range)


class Page(object):
    def __init__(self, object_list, number, paginator):
        self.object_list = object_list
        self.number = number
        self.paginator = paginator

    def __repr__(self):
        return '<Page %s of %s>' % (self.number, self.paginator.total_pages)

    def has_next(self):
        return self.number < self.paginator.total_pages

    def has_previous(self):
        return self.number > 1

    def has_other_pages(self):
        return self.has_previous() or self.has_next()

    def __next_page_number(self):
        return self.number + 1
    next_page_number = property(__next_page_number)

    def __previous_page_number(self):
        return self.number - 1
    previous_page_number = property(__previous_page_number)

    def __start_index(self):
        # Special case, return zero if no items.
        if self.paginator.count == 0:
            return 0
        return (self.paginator.per_page_limit * (self.number - 1)) + 1
    start_index = property(__start_index)

    def __end_index(self):
        # Special case for the last page
        if self.number == self.paginator.total_pages:
            return self.paginator.count
        return self.number * self.paginator.per_page_limit
    end_index = property(__end_index)
