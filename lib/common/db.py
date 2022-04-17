import sqlite3, datetime
from typing import NamedTuple


class UpdateData(NamedTuple):
    retailer:   str
    query:      str
    title:      str
    url:        str
    price:      int

class Entry(NamedTuple):
    retailer:   str
    query:      str
    title:      str
    url:        str
    price:      int
    timestamp:  datetime.datetime


class Snapshot:
    def __init__(self, db):
        self._db = db
        self._update_data = []

    def add_data(self, **kwargs):
        self._update_data.append(UpdateData(**kwargs) )

    def commit(self):
        id_snapshot = self._db._get_latest_snapshot_id() + 1
        timestamp = datetime.datetime.now()
        for x in self._update_data:
            self._db.con.execute('INSERT INTO items_prices VALUES (?,?,?,?,?,?,?)', (id_snapshot, timestamp, x.retailer, x.query, x.title,x.url, x.price))
        self._db.con.commit()



class Db:
    def __init__(self):
        self.con = sqlite3.connect('config/scraper.db')
        self.con.execute('CREATE TABLE IF NOT EXISTS items_prices (id_snapshot integer, date text, retailer text, query text, title text, url text, price integer )')
        self.con.commit()

    def _get_latest_snapshot_id(self):
        cur = self.con.cursor()
        cur.execute('SELECT id_snapshot FROM items_prices ORDER BY id_snapshot DESC LIMIT 1')
        entry = cur.fetchone()
        return entry[0] if entry else 0


    def create_snapshot_sink(self):
        return Snapshot(self)


    def get_latest(self, query: str) -> list[Entry]:
        entries: list[Entry] = []

        last_snapshot_id = self._get_latest_snapshot_id()
        if last_snapshot_id == 0:
            return entries

        result = self.con.execute('SELECT retailer,title,url,price,date,query FROM items_prices WHERE query = ? AND id_snapshot = ?', (query,last_snapshot_id))
        for row in result:
            entries.append( Entry(query=row[5],
                        retailer=row[0],
                        title=row[1],
                        url=row[2],
                        price=row[3],
                        timestamp=row[4]))
        return sorted(entries,key=lambda x: x.price)[:5]
        
