import requests

class MiningRewardsSource:
    def __init__(self, kwh_cost_usd: float):
        self._mining_data =  {
            151 : requests.get(f'https://whattomine.com/coins/151.json', params=dict(hr=1, p=1, fee=0, cost=kwh_cost_usd, cost_currency='USD', hcost=0.0, span_br='1h', span_d=24)).json()
        }

    
    def get_daily_net_profit(self, algorithm: int, hashrate: float, power: float, fee_pc: float=1) -> float:
        """get daily rewards in USD"""
        entry = self._mining_data[algorithm]
        daily_revenue_1_mh = float(entry['revenue'].replace('$',''))
        daily_cost_1_watt_hour = float(entry['cost'].replace('$',''))
        return (daily_revenue_1_mh * hashrate * (1.0 - fee_pc / 100.0)) - (daily_cost_1_watt_hour * power)
