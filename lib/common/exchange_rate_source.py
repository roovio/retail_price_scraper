import requests

class ExchangeRateSource:

    def _binance_get_current_price(self,sym:str) -> float:
        return float(requests.get('https://api.binance.com/api/v3/avgPrice', params=dict(symbol=sym) ).json()['price'])

    def __init__(self):
        self._uah_usd = 1 / self._binance_get_current_price('USDTUAH')
        self._btc_usd = self._binance_get_current_price('BTCUSDT')

    def get_UAH_USD(self) -> float:
        return self._uah_usd

    def get_BTC_USD(self) -> float:
        return self._btc_usd
