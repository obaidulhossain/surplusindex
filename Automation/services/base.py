# auction_scraper/services/base.py

import requests

class BaseScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0",
            "X-Requested-With": "XMLHttpRequest",
        })

    def get(self, url, params=None):
        return self.session.get(url, params=params, timeout=30)

    def post(self, url, data=None):
        return self.session.post(url, data=data, timeout=30)
