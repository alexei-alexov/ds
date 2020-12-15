import re
from requests import HTTPError

from parsing.utils import get_list_page

link_re = re.compile(r'href="(https://auto.ru/cars/used/sale/.*?)"')


class ListParser:

    def __init__(self, use_proxy=True, pages=(1, 10)):
        self.use_proxy = use_proxy
        self.pages = pages

    def parse(self):
        ids_count = 0
        page_no = self.pages[0] if self.pages else 1
        buffer = []
        while self.is_in_page_bounds(page_no):
            visited = set()
            try:
                r = get_list_page(page_no, use_proxy=self.use_proxy)
            except HTTPError:
                print('Cannot load page: %d' % (page_no,))
                raise
            for m in link_re.finditer(r.text):
                _id = m.group(1).split('/')[-2]
                if _id not in visited:
                    ids_count += 1
                    buffer.append(_id)
                    visited.add(_id)

            print('Finished loading of %d page' % (page_no, ))
            print('Found %d ids on it' % (len(buffer),))

            for _id in buffer:
                yield _id
            page_no += 1
            del buffer[:]
        print('Fetched %d ids' % (ids_count,))

    def is_in_page_bounds(self, page: int) -> bool:
        """Check is given page is in target pages bounds"""
        if not self.pages:
            return True
        return self.pages[0] <= page <= self.pages[1]



if __name__ == '__main__':
    parser = ListParser(pages=[1, 3])
    parser.parse()
