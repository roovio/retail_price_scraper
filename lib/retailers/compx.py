from lib.retailers.interface import Retailer, ItemPosition
from lib.common.fuzzy_matcher import matches_search_keyword, get_query_string_for_search_keyword
import requests
from bs4 import BeautifulSoup

#import lib.common.more_verbose_http_requests


class Compx(Retailer):

    def __init__(self):
        self._session = requests.Session()


    def get_prices(self, search_keyword: str) -> list[ItemPosition]:
        base_url= 'https://compx.com.ua'
        request = requests.Request('GET',base_url+ '/katalog/search/filter/page=all/', params={'q':get_query_string_for_search_keyword(search_keyword)}, )
        response = self._session.send(request.prepare())
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

