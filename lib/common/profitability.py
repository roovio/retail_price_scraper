
from lib.common.mining_rewards_source import MiningRewardsSource
from lib.common.exchange_rate_source import ExchangeRateSource
import yaml

hashrate_conf = yaml.safe_load(open('config/hashrate.yml', 'r'))
electricity_conf = yaml.safe_load(open('config/electricity.yml', 'r'))

class Profitability:
    def __init__(self):
        exchange_rate_source = ExchangeRateSource()
        self._mining_rewards_source = MiningRewardsSource(kwh_cost_usd=electricity_conf['cost'] * exchange_rate_source.get_UAH_USD())

    def get_daily_profit_usd(self, gpu: str) -> float:
        """get daily revenue in USD"""

        algorithm = 151

        hashrate_table_entry = hashrate_conf[algorithm][gpu]
        hashrate,power = hashrate_table_entry.split(',')

        return self._mining_rewards_source.get_daily_net_profit(
            algorithm=algorithm,
            hashrate=float(hashrate),
            power=float(power)            
            )
        
