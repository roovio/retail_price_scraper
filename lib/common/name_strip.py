import yaml, re

class NameStrip:
    def __init__(self):
        conf = yaml.safe_load(open('config/scraper.yml', 'r'))
        self.ignore_list = []
        if 'strip' in conf:
            self._strip = conf['strip']


    def strip(self, item: str):
        for strip_pattern in self._strip:
            item = item.replace(strip_pattern, '')
        return item.strip()
