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
          (normalized_name is set from name when saving; do not supply it.)
        }
        Return empty items list on failure, never raise.
        """
        pass

    async def run(self, store: FlyerStore):
        from asgiref.sync import sync_to_async
        from django.utils import timezone
        from playwright.async_api import async_playwright

        from scrapers.models import FlyerCycle, FlyerItem, ScrapeLog

        @sync_to_async
        def create_running_log():
            return ScrapeLog.objects.create(
                store=store,
                started_at=timezone.now(),
                status=ScrapeLog.STATUS_RUNNING,
            )

        @sync_to_async
        def persist_region(province, result):
            if not result.get('items'):
                return 0
            valid_from = result.get('valid_from')
            valid_to = result.get('valid_to')
            if valid_from is None or valid_to is None:
                return 0

            FlyerCycle.objects.filter(
                store=store,
                province=province,
                is_current=True,
            ).update(is_current=False)

            cycle = FlyerCycle.objects.create(
                store=store,
                province=province,
                valid_from=valid_from,
                valid_to=valid_to,
                is_current=True,
            )

            items = []
            for raw in result['items']:
                row = dict(raw)
                row.pop('normalized_name', None)
                name = row.get('name')
                if not name or not str(name).strip():
                    continue
                row['name'] = str(name).strip()
                # DB requires normalized_name NOT NULL; keep flyer text intact for downstream matching.
                row['normalized_name'] = row['name']
                items.append(
                    FlyerItem(
                        store=store,
                        cycle=cycle,
                        province=province,
                        **row,
                    ),
                )
            FlyerItem.objects.bulk_create(
                items,
                ignore_conflicts=True,
            )
            return len(items)

        @sync_to_async
        def mark_log_success(log_pk, total_items):
            ScrapeLog.objects.filter(pk=log_pk).update(
                status=ScrapeLog.STATUS_SUCCESS,
                items_scraped=total_items,
                finished_at=timezone.now(),
            )

        @sync_to_async
        def mark_log_failed(log_pk, message):
            ScrapeLog.objects.filter(pk=log_pk).update(
                status=ScrapeLog.STATUS_FAILED,
                error_message=message,
                finished_at=timezone.now(),
            )

        log = await create_running_log()
        log_pk = log.pk
        total = 0
        try:
            flyer_urls = await self.get_flyer_urls()

            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-blink-features=AutomationControlled',
                    ],
                )
                context = await browser.new_context(
                    user_agent=(
                        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 '
                        'like Mac OS X) AppleWebKit/605.1.15 '
                        '(KHTML, like Gecko) Version/17.0 '
                        'Mobile/15E148 Safari/604.1'
                    ),
                    viewport={'width': 390, 'height': 844},
                    locale='en-CA',
                    timezone_id='America/Winnipeg',
                )

                for province, url in flyer_urls.items():
                    page = await context.new_page()
                    result = await self.scrape_region(
                        page,
                        url,
                        province,
                    )
                    await page.close()

                    total += await persist_region(province, result)

                await browser.close()

            await mark_log_success(log_pk, total)

        except Exception as e:
            await mark_log_failed(log_pk, str(e))
