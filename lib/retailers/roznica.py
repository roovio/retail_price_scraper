from lib.retailers.interface import Retailer, ItemPosition
from lib.common.fuzzy_matcher import matches_search_keyword, get_query_string_for_search_keyword
import requests
from bs4 import BeautifulSoup

#import lib.common.more_verbose_http_requests


class Roznica(Retailer):

    def __init__(self):
        self._session = requests.Session()


    def get_prices(self, search_keyword: str) -> list[ItemPosition]:
        base_url = 'https://www.roznica.com.ua'
        request = requests.Request('GET',base_url +'/videokarty-c190', params=dict(q=134923), cookies=dict(searchdatasrc=get_query_string_for_search_keyword(search_keyword)) )
        response = self._session.send(request.prepare())
        response.raise_for_status()
        parser = BeautifulSoup(response.text, 'html.parser')
        r = []
        item_container_node = parser.find(class_='items-container')
        for item_node in item_container_node.find_all('li', class_='item'):
            title_node = item_node.find('h6')
            title = title_node.text.strip()
            url = base_url + title_node.find('a').get('href')
            price = int(item_node.find(class_='actual-price').text.replace(' ','').replace('грн','').strip())
            if matches_search_keyword(title, search_keyword):
                r.append(ItemPosition(title=title,price=price,url=url))
        return r

