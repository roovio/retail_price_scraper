import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from lib.retailers.interface import Retailer, ItemPosition
from lib.common.fuzzy_matcher import matches_search_keyword, get_query_string_for_search_keyword

class Comtrading(Retailer):

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        self._driver = webdriver.Chrome(options=options)

    def get_prices(self, search_keyword: str) -> list[ItemPosition]:
        r = []
        self._driver.get('https://comtrading.ua/komputery-seti-275/komplektuuschie-dlya-pk-334/videokarty-338/?s='+get_query_string_for_search_keyword(search_keyword) )
        for e in WebDriverWait(self._driver,60).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'product-wrap'))):           
            node_title = e.find_element(By.CLASS_NAME, 'product-name')
            title = node_title.text.strip()
            url = node_title.get_property('href')
            price = e.find_element(By.CLASS_NAME, 'product-price').text.strip()
            m = re.match(r'^([\d ]+)₴', price)
            if m:
                price = int(m[1].replace(' ',''))
                if matches_search_keyword(title, search_keyword):
                    r.append(ItemPosition(title=title,price=price,url=url))
            
        return r
