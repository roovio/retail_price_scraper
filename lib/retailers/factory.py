from typing import Iterable
from lib.retailers.interface import Retailer
from lib.retailers.compx import Compx
from lib.retailers.comtrading import Comtrading
from lib.retailers.utc import Utc
from lib.retailers.telemart import Telemart
from lib.retailers.roznica import Roznica

class Factory:
    def __init__(self):
        self._map = dict(
            compx=Compx(),
            comtrading=Comtrading(),
            utc=Utc(),
            telemart=Telemart(),
            roznica=Roznica(),
            )

    def get_retailer_list(self) -> str:
        return self._map.keys()

    def get_retailer_iterator(self) -> Iterable[tuple[str,Retailer]]:
        for name, obj in self._map.items():
            yield name, obj

    def get_retailer(self, name: str) -> Retailer:
        return self._map[name]
