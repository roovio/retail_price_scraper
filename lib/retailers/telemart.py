from lib.retailers.interface import Retailer, ItemPosition
from lib.common.fuzzy_matcher import matches_search_keyword, get_query_string_for_search_keyword
import requests, functools
from bs4 import BeautifulSoup

#import lib.common.more_verbose_http_requests


class Telemart(Retailer):

    def __init__(self):
        self._session = requests.Session()

    def _get_page(self, search_keyword: str, page_index: int) -> list[ItemPosition]:
        base_url= 'https://telemart.ua'
        request = requests.Request('GET',base_url+ '/ua/search/', params={'search_que':get_query_string_for_search_keyword(search_keyword), 'p': page_index}, )
        response = self._session.send(request.prepare())
        response.raise_for_status()
        # print(response.text)
        parser = BeautifulSoup(response.text, 'html.parser')
        r = []
        for item_node in parser.find_all(class_='b-i-product-inner'):
            availability = item_node.find(class_='b-i-product-mid-meta').text.strip()
            if availability == 'Є в наявності' or availability == 'Закінчується':
                title_node = item_node.find(class_='b-i-product-name')
                title = title_node.text.strip()
                url = title_node.find('a').get('href')
                price = int(item_node.find(class_='b-price').text.replace(' ','').replace('грн','').strip())
                if matches_search_keyword(title, search_keyword):
                    r.append(ItemPosition(title=title,price=price,url=url))
        return r


    def get_prices(self, search_keyword: str) -> list[ItemPosition]:
        results_per_page = [ self._get_page(search_keyword, i) for i in range(1,4) ]
        return functools.reduce(lambda x,y: x + y, results_per_page)

