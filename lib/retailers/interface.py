from abc import abstractmethod

class Retailer(object):
    @abstractmethod
    def get_prices(self, search_keyword: str) -> list[tuple[str,float]]:
        """return a list of pairs (item name, price) """

