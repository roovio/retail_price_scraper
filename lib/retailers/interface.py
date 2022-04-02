from abc import abstractmethod
from typing import NamedTuple

class ItemPosition(NamedTuple):
    title:  str
    price:  float
    url:    str = ""

class Retailer(object):
    @abstractmethod
    def get_prices(self, search_keyword: str) -> list[ItemPosition]:
        """return a list of pairs (item name, price) """

