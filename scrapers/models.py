"""
Models for the flyer scraper.

These tables are owned exclusively by the Django scraper app. The Supabase
PostgreSQL database is shared with the Cartio Laravel app, but Django
must never alter or migrate any non-scrapers tables. Each model declares
an explicit db_table and managed=True to make ownership explicit.
"""
from django.db import models


class FlyerStore(models.Model):
    REGION_CHOICES = [
        ('CA', 'Canada'),
        ('US', 'United States'),
    ]

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    region = models.CharField(max_length=10, choices=REGION_CHOICES)
    flyer_url = models.URLField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'flyer_stores'
        managed = True

    def __str__(self) -> str:
        return f'{self.name} ({self.region})'


class FlyerStoreBranch(models.Model):
    id = models.BigAutoField(primary_key=True)
    store = models.ForeignKey(
        FlyerStore,
        on_delete=models.CASCADE,
        related_name='branches',
    )
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    latitude = models.FloatField()
    longitude = models.FloatField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'flyer_store_branches'
        managed = True
        indexes = [
            models.Index(fields=['province']),
            models.Index(fields=['latitude', 'longitude']),
        ]

    def __str__(self) -> str:
        return f'{self.store.name} — {self.city}, {self.province}'


class FlyerCycle(models.Model):
    id = models.BigAutoField(primary_key=True)
    store = models.ForeignKey(
        FlyerStore,
        on_delete=models.CASCADE,
        related_name='flyer_cycles',
    )
    province = models.CharField(max_length=50, null=True, blank=True)
    valid_from = models.DateField()
    valid_to = models.DateField()
    scraped_at = models.DateTimeField(auto_now_add=True)
    is_current = models.BooleanField(default=True)

    class Meta:
        db_table = 'flyer_cycles'
        managed = True
        indexes = [
            models.Index(fields=['store', 'is_current']),
            models.Index(fields=['valid_to']),
            models.Index(fields=['province']),
        ]

    def __str__(self) -> str:
        region = self.province or 'national'
        return f'{self.store.name} ({region}) {self.valid_from}–{self.valid_to}'


class FlyerItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    store = models.ForeignKey(
        FlyerStore,
        on_delete=models.PROTECT,
        related_name='items',
    )
    province = models.CharField(max_length=50, null=True, blank=True)
    cycle = models.ForeignKey(
        FlyerCycle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='flyer_items',
    )
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    original_price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
    )
    unit = models.CharField(max_length=50, null=True, blank=True)
    valid_from = models.DateField(null=True, blank=True)
    valid_to = models.DateField(null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)
    raw_text = models.TextField(null=True, blank=True)
    scraped_at = models.DateTimeField(auto_now_add=True)

    # Flyer location fields — used to zoom/highlight this item when
    # rendering the flyer HTML page in Cartio. bbox values come from
    # Playwright's element.boundingBox(); page_width/page_height come
    # from page.viewport_size. Stored as raw pixels — Cartio converts
    # to percentages at render time.
    flyer_page_url = models.URLField(null=True, blank=True)
    bbox_x = models.FloatField(null=True, blank=True)
    bbox_y = models.FloatField(null=True, blank=True)
    bbox_width = models.FloatField(null=True, blank=True)
    bbox_height = models.FloatField(null=True, blank=True)
    page_width = models.FloatField(null=True, blank=True)
    page_height = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'flyer_items'
        managed = True

    def __str__(self) -> str:
        return self.name


class ScrapeLog(models.Model):
    STATUS_RUNNING = 'running'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_RUNNING, 'Running'),
        (STATUS_SUCCESS, 'Success'),
        (STATUS_FAILED, 'Failed'),
    ]

    id = models.BigAutoField(primary_key=True)
    store = models.ForeignKey(
        FlyerStore,
        on_delete=models.CASCADE,
        related_name='scrape_logs',
    )
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField(null=True, blank=True)
    items_scraped = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'flyer_scrape_logs'
        managed = True

    def __str__(self) -> str:
        return f'{self.store.name} — {self.status} @ {self.started_at:%Y-%m-%d %H:%M}'
