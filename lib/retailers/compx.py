from lib.retailers.interface import Retailer, ItemPosition
from lib.common.fuzzy_matcher import matches_search_keyword, get_query_string_for_search_keyword
import requests
from bs4 import BeautifulSoup
import functools

#import lib.common.more_verbose_http_requests


class Compx(Retailer):

    def __init__(self):
        self._session = requests.Session()


    def _get_page(self, search_keyword: str, page_index: int) -> list[ItemPosition]:
        base_url= 'https://compx.com.ua'
        request = requests.Request('GET',base_url+ f'/katalog/search/filter/page={page_index}/', params={'q':get_query_string_for_search_keyword(search_keyword)}, )
        response = self._session.send(request.prepare())
        if response.status_code == 404:
            return None
        response.raise_for_status()
        parser = BeautifulSoup(response.text, 'html.parser')
        r = []
        for item_main_div in parser.find_all(class_='catalogCard-main'):
            title_node = item_main_div.find(class_='catalogCard-title')
            title = title_node.text.strip()
            url = base_url + title_node.find('a').get('href')
            price = int(item_main_div.find(class_='catalogCard-price').text.replace(' ','').replace('грн','').strip())
            if matches_search_keyword(title, search_keyword):
                r.append(ItemPosition(title=title,price=price,url=url))
        return r


    def get_prices(self, search_keyword: str) -> list[ItemPosition]:
        results_per_page = []
        for page_index in range(1,10):
            p = self._get_page(search_keyword, page_index)
            if p is None:
                break
            results_per_page.append(p)
        return functools.reduce(lambda x,y: x + y, results_per_page)

