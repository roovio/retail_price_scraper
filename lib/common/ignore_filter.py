import yaml, re

class IgnoreFilter:
    def __init__(self):
        conf = yaml.safe_load(open('config/scraper.yml', 'r'))
        self.ignore_list = []
        if 'ignore' in conf:
            self._ignore_list = conf['ignore']


    def is_ignored(self, item: str):
        for ignore_pattern in self._ignore_list:
            if re.search(ignore_pattern, item):
                return True
        return False
