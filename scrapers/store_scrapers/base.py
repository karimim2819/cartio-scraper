from abc import ABC, abstractmethod

from playwright.async_api import Page

from scrapers.models import FlyerStore


class BaseScraper(ABC):

    store_name: str = None
    regions: dict = {}
    # regions format: { 'Province Name': 'flyer_url' }
    # National flyers use: { None: 'flyer_url' }

    @abstractmethod
    async def get_flyer_urls(self) -> dict:
        """
        Return { province_label: flyer_url }.
        National flyers return { None: flyer_url }.
        """
        pass

    @abstractmethod
    async def scrape_region(
        self,
        page: Page,
        flyer_url: str,
        province: str | None,
    ) -> dict:
        """
        Scrape one flyer page. Must return:
        {
          'valid_from': date | None,
          'valid_to': date | None,
          'items': [ {
            name, price, original_price, unit,
            flyer_page_url, image_url, raw_text,
            bbox_x, bbox_y, bbox_width, bbox_height,
            page_width, page_height
          } ]
        }
        Return empty items list on failure, never raise.
        """
        pass

    async def run(self, store: FlyerStore):
        """
        Orchestration method — implemented in a later MR.
        """
        pass
