# auction_scraper/services/realauction.py

from .base import BaseScraper

class RealAuctionScraper(BaseScraper):

    AJAX_ENDPOINT = "/index.cfm"

    def __init__(self, source):
        super().__init__()
        self.source = source
        self.base_url = self.source.preview_url.split("/index.cfm")[0]

    def initialize_session(self):
        """Load preview page to set cookies"""
        self.get(
            self.source.preview_url,
            params={
                "zaction": "AUCTION",
                "zmethod": "PREVIEW",
                "AuctionDate": self.source.auction_date
            }
        )

    def ajax_load(self, ref="W"):
        """Initial AJAX load"""
        return self.post(
            self.base_url + self.AJAX_ENDPOINT,
            data={
                "zaction": "AUCTION",
                "ZMETHOD": "UPDATE",
                "FNC": "LOAD",
                "ref": ref,
                "AuctionDate": self.source.auction_date,
            }
        )

    def ajax_update(self, ref, alb_ids):
        """Pagination update"""
        return self.post(
            self.base_url + self.AJAX_ENDPOINT,
            data={
                "zaction": "AUCTION",
                "ZMETHOD": "UPDATE",
                "FNC": "UPDATE",
                "ref": ref,
                "ALB": ",".join(alb_ids),
            }
        )
