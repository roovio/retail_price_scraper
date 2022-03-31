import argparse, yaml, logging
from logging import error, info
from lib.retailers.interface import Retailer
from lib.retailers.factory import Factory as RetailerFactory
import pandas as pd

conf = yaml.safe_load(open('config/scraper.yml', 'r'))


def show(search_item: str, retailer_name: str):

    retailer_factory =  RetailerFactory()

    info('Scraping using search term: %s', search_item)

    d = []
    for name,retailer in retailer_factory.get_retailer_iterator() :
        if retailer_name is None or retailer_name == name:
            scrape_result: list[tuple[str,float]] = retailer.get_prices(search_item)
            for item_name, item_price in scrape_result:
                d.append(dict(retailer=name,search=search_item,item=item_name,price=item_price))
    df = pd.DataFrame.from_dict(d)
    if len(df):
        df = df.sort_values('price',ascending=True)
        print(df.to_string(index=False))
    else:
        info('No results')


def main():
    #log_msg_format = '%(asctime)s  %(levelname)s  %(message)s'
    log_msg_format = '%(levelname)s : %(message)s'
    logging.basicConfig(format=log_msg_format, level=conf['log_level'] if 'log_level' in conf else logging.WARNING)

    parser = argparse.ArgumentParser()

    parser.add_argument('--item', type=str, help='item substring to search')
    parser.add_argument('--retailer', type=str, help='retailer id. If unset show from all available retailers')
    
    args = parser.parse_args()

    if args.item:
        show(args.item, args.retailer)
    else:
        error('item argument not specified')



if __name__ == '__main__':
    main()
