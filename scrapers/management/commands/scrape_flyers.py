"""
Management command stub: `python manage.py scrape_flyers [--store NAME]`

For each target store this command opens a ScrapeLog row, calls
`scrape_store(store)` (currently a no-op), and closes the log with
either 'success' or 'failed'. The actual Playwright scraping logic
will be implemented in scrape_store.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone

from scrapers.models import FlyerCycle, FlyerStore, ScrapeLog


def scrape_store(store: FlyerStore) -> int:
    """Scrape a single store and return the number of items scraped.

    Stub for now — Playwright logic to be added.
    """
    pass


class Command(BaseCommand):
    help = 'Scrape grocery flyers for active stores (or a single store).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--store',
            type=str,
            default=None,
            help='Only scrape the FlyerStore with this exact name.',
        )

    def handle(self, *args, **options):
        store_name = options.get('store')

        if store_name:
            stores = FlyerStore.objects.filter(name=store_name)
            if not stores.exists():
                self.stdout.write(
                    self.style.ERROR(f'No FlyerStore found with name: {store_name}')
                )
                return
        else:
            stores = FlyerStore.objects.filter(is_active=True)

        total = stores.count()
        self.stdout.write(f'Scraping {total} store(s)...')

        for store in stores:
            today = timezone.now().date()
            active_cycle = FlyerCycle.objects.filter(
                store=store,
                is_current=True,
                valid_to__gte=today,
            ).exists()

            if active_cycle:
                self.stdout.write(f'Skipping {store.name} — flyer still valid')
                continue

            self.stdout.write(f'→ {store.name} ({store.region}) starting...')

            log = ScrapeLog.objects.create(
                store=store,
                started_at=timezone.now(),
                status=ScrapeLog.STATUS_RUNNING,
            )

            try:
                items_scraped = scrape_store(store) or 0
            except Exception as exc:  # noqa: BLE001 — surface any scraper failure
                log.status = ScrapeLog.STATUS_FAILED
                log.error_message = str(exc)
                log.finished_at = timezone.now()
                log.save(update_fields=['status', 'error_message', 'finished_at'])
                self.stdout.write(
                    self.style.ERROR(f'  ✗ {store.name} failed: {exc}')
                )
                continue

            # TODO: create FlyerCycle(valid_from, valid_to) after scraping

            log.status = ScrapeLog.STATUS_SUCCESS
            log.items_scraped = items_scraped
            log.finished_at = timezone.now()
            log.save(update_fields=['status', 'items_scraped', 'finished_at'])
            self.stdout.write(
                self.style.SUCCESS(
                    f'  ✓ {store.name} done — {items_scraped} item(s)'
                )
            )

        self.stdout.write(self.style.SUCCESS('All scrapes complete.'))
