# -*- coding: utf-8 -*-

from .paginator import Paginator


class Pagination(object):

    def __init__(self, paginator, page, per_page, total, items):

        self.paginator = paginator
        self.page = page
        self.per_page = per_page
        self.total = total
        self.items = items

    @property
    def pages(self):
        pages = self.total
        return pages

    def prev(self, error_out=False):
        return Pagination(self.paginator, self.page-1, self.per_page, self.paginator.total_pages, self.paginator.page(self.page-1).object_list)

    @property
    def prev_num(self):
        return self.page - 1

    @property
    def has_prev(self):
        return self.page > 1

    def next(self, error_out=False):
        return Pagination(self.paginator, self.page+1, self.per_page, self.paginator.total_pages, self.paginator.page(self.page+1).object_list)

    @property
    def has_next(self):
        return self.page < self.pages

    @property
    def next_num(self):
        return self.page + 1

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and \
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num
