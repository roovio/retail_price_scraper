from lib.retailers.interface import Retailer
from lib.common.fuzzy_matcher import matches_search_keyword, get_query_string_for_search_keyword
import requests
from bs4 import BeautifulSoup

#import lib.common.more_verbose_http_requests


class Utc(Retailer):

    def __init__(self):
        self._session = requests.Session()


    def get_prices(self, search_keyword: str) -> list[tuple[str,float]]:
        request = requests.Request('GET','https://utc.co.ua/all-products', params={'keyword':get_query_string_for_search_keyword(search_keyword)}, )
        response = self._session.send(request.prepare())
        response.raise_for_status()
        parser = BeautifulSoup(response.text, 'html.parser')
        r = []
        for item_main_div in parser.find_all(class_='products_item'):
            title = item_main_div.find(class_='product_name').text.strip()
            price = int(item_main_div.find(class_='price_container').text.replace(' ','').replace('грн','').strip())
            if matches_search_keyword(title, search_keyword):
                r.append((title,price))
        return r

