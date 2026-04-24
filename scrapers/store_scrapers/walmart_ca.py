import asyncio

from playwright.async_api import async_playwright

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
