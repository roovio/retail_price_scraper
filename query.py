import argparse, yaml
from lib.common.db import Db
from lib.common.ignore_filter import IgnoreFilter
from lib.common.profitability import Profitability
from lib.common.exchange_rate_source import ExchangeRateSource

import pandas as pd

conf = yaml.safe_load(open('config/scraper.yml', 'r'))



def show_latest_prices():

    db = Db()
    ignore_filter = IgnoreFilter()
    profitability = Profitability()
    exchange_rate_source = ExchangeRateSource()

    d=[]
    for s in conf['search_keywords']:
        for e in db.get_latest(s):
            if not ignore_filter.is_ignored(e.title):
                daily_profit_usd = profitability.get_daily_profit_usd(s)
                monthly_profit_usd = daily_profit_usd * 30
                roi_months = e.price * exchange_rate_source.get_UAH_USD()  / monthly_profit_usd
                d.append( dict(
                    retailer=e.retailer,
                    search=e.query,
                    item=e.title,
                    price=e.price,
                    price_usd=round(e.price *  exchange_rate_source.get_UAH_USD()) ,
                    url=e.url,
                    roi_m=round(roi_months,1),
                    daily_profit_usd=round(daily_profit_usd,2),
                    ) )
    df = pd.DataFrame.from_dict(d)
    if len(df):
        df = df.sort_values('roi_m',ascending=True)
        print(df.to_string(index=False,columns=['retailer', 'search','item', 'price', 'price_usd', 'roi_m', 'daily_profit_usd']))



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--latest', action='store_const', const='True', help='Show latest prices for all search keywords')
    # parser.add_argument('--history', action='store_const', const='True', help='Show price movement dynamics. Requires --item.')
    # parser.add_argument('--item', type=str, help='Search keyword')
    
    args = parser.parse_args()

    if args.latest:
        show_latest_prices()
    # elif args.history:
    #     show_price_dynamics(query=args.item)


if __name__ == '__main__':
    main()
