from django.contrib import admin

from .models import FlyerItem, FlyerStore, ScrapeLog


@admin.register(FlyerStore)
class FlyerStoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'is_active', 'flyer_url')
    list_filter = ('region', 'is_active')
    search_fields = ('name',)


@admin.register(FlyerItem)
class FlyerItemAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'store',
        'price',
        'valid_from',
        'valid_to',
        'flyer_page_url',
        'scraped_at',
    )
    list_filter = ('store', 'valid_from', 'valid_to')
    search_fields = ('name', 'raw_text')


@admin.register(ScrapeLog)
class ScrapeLogAdmin(admin.ModelAdmin):
    list_display = (
        'store',
        'status',
        'items_scraped',
        'started_at',
        'finished_at',
    )
    list_filter = ('status', 'store')
