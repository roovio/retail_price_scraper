import yaml
from lib.retailers.interface import ItemPosition
from lib.retailers.factory import Factory as RetailerFactory
from lib.common.db import Db


def main():
    conf = yaml.safe_load(open('config/scraper.yml', 'r'))

    retailer_factory =  RetailerFactory()
    db = Db()
    snapshot = db.create_snapshot_sink()
    for query  in conf['search_keywords']:
        print(query, end='',flush=True)
        for name,retailer in retailer_factory.get_retailer_iterator() :
            print('.', end='',flush=True)
            scrape_result: list[ItemPosition] = retailer.get_prices(query)
            for item_pos in scrape_result:
                snapshot.add_data(retailer=name, query=query, title=item_pos.title, url=item_pos.url, price=item_pos.price )
        print()
    snapshot.commit()

if __name__ == '__main__':
    main()
    