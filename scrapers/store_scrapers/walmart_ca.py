import asyncio
from decimal import Decimal, InvalidOperation

from dateutil import parser as dateparser
from playwright.async_api import async_playwright

from scrapers.store_scrapers.base import BaseScraper

CANDIDATE_SELECTORS = [
    '[data-automation="flyer-item"]',
    '[class*="flyer"]',
    '[class*="product"]',
    '[class*="item"]',
    'article',
    'li[class*="tile"]',
]


async def inspect_walmart_flyer():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
            ],
        )
        context = await browser.new_context(
            user_agent=(
                'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) '
                'AppleWebKit/605.1.15 (KHTML, like Gecko) '
                'Version/17.0 Mobile/15E148 Safari/604.1'
            ),
            viewport={'width': 390, 'height': 844},
            locale='en-CA',
            timezone_id='America/Winnipeg',
        )
        page = await context.new_page()
        await page.goto('https://www.walmart.ca/en/flyer')
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(5000)

        print(f"Page title: {await page.title()}")

        for selector in CANDIDATE_SELECTORS:
            elements = await page.query_selector_all(selector)
            print(f"\nSelector '{selector}': {len(elements)} found")
            for el in elements[:3]:
                print(await el.inner_text())
                print(await el.bounding_box())

        html = await page.content()
        with open('/tmp/walmart_flyer_debug.html', 'w') as f:
            f.write(html)
        print("\nHTML saved to /tmp/walmart_flyer_debug.html")

        await browser.close()


if __name__ == '__main__':
    asyncio.run(inspect_walmart_flyer())


class WalmartCanadaScraper(BaseScraper):

    store_name = 'Walmart Canada'

    regions = {
        'Ontario': 'https://www.walmart.ca/en/flyer',
        'Quebec': 'https://www.walmart.ca/en/flyer',
        'British Columbia': 'https://www.walmart.ca/en/flyer',
        'Manitoba': 'https://www.walmart.ca/en/flyer',
        'New Brunswick': 'https://www.walmart.ca/en/flyer',
    }
    # NOTE: Update region URLs to real region-specific flyer URLs
    # after DOM inspection confirms how Walmart serves regional flyers.

    async def get_flyer_urls(self) -> dict:
        return self.regions

    async def scrape_region(self, page, flyer_url, province):
        try:
            await page.goto(flyer_url)
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(3000)

            # SELECTOR: update after DOM inspection
            date_el = await page.query_selector('[class*="validity"]')
            valid_from, valid_to = None, None
            if date_el:
                date_text = await date_el.inner_text()
                # Attempt to parse date range e.g. "Apr 23 - Apr 29"
                try:
                    parts = date_text.split('-')
                    valid_from = dateparser.parse(
                        parts[0].strip(),
                    ).date()
                    valid_to = dateparser.parse(
                        parts[1].strip(),
                    ).date()
                except Exception:
                    pass

            # SELECTOR: update after DOM inspection
            item_els = await page.query_selector_all(
                '[data-automation="flyer-item"]',
            )

            viewport = page.viewport_size
            page_width = viewport['width'] if viewport else None
            page_height = viewport['height'] if viewport else None

            items = []
            for el in item_els:
                try:
                    # SELECTOR: update after DOM inspection
                    name_el = await el.query_selector(
                        '[class*="title"], [class*="name"], h3, h4',
                    )
                    name = (
                        await name_el.inner_text()
                        if name_el
                        else None
                    )

                    # SELECTOR: update after DOM inspection
                    price_el = await el.query_selector(
                        '[class*="price"]:not([class*="original"])',
                    )
                    price = None
                    if price_el:
                        raw = (
                            (await price_el.inner_text())
                            .replace('$', '')
                            .strip()
                        )
                        try:
                            price = Decimal(raw)
                        except InvalidOperation:
                            pass

                    # SELECTOR: update after DOM inspection
                    orig_el = await el.query_selector(
                        '[class*="original"], [class*="was"],'
                        '[class*="strike"]',
                    )
                    original_price = None
                    if orig_el:
                        raw = (
                            (await orig_el.inner_text())
                            .replace('$', '')
                            .strip()
                        )
                        try:
                            original_price = Decimal(raw)
                        except InvalidOperation:
                            pass

                    # SELECTOR: update after DOM inspection
                    unit_el = await el.query_selector(
                        '[class*="unit"], [class*="each"],'
                        '[class*="per"]',
                    )
                    unit = (
                        await unit_el.inner_text()
                        if unit_el
                        else None
                    )

                    # SELECTOR: update after DOM inspection
                    img_el = await el.query_selector('img')
                    image_url = (
                        await img_el.get_attribute('src')
                        if img_el
                        else None
                    )

                    bbox = await el.bounding_box()

                    items.append({
                        'name': name,
                        'price': price,
                        'original_price': original_price,
                        'unit': unit,
                        'image_url': image_url,
                        'raw_text': await el.inner_text(),
                        'flyer_page_url': page.url,
                        'bbox_x': bbox['x'] if bbox else None,
                        'bbox_y': bbox['y'] if bbox else None,
                        'bbox_width': bbox['width'] if bbox else None,
                        'bbox_height': bbox['height'] if bbox else None,
                        'page_width': page_width,
                        'page_height': page_height,
                    })
                except Exception:
                    continue

            return {
                'valid_from': valid_from,
                'valid_to': valid_to,
                'items': items,
            }

        except Exception:
            return {'valid_from': None, 'valid_to': None, 'items': []}
