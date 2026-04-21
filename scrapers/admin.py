from django.contrib import admin

from .models import FlyerCycle, FlyerItem, FlyerStore, FlyerStoreBranch, ScrapeLog


@admin.register(FlyerStore)
class FlyerStoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'is_active', 'flyer_url')
    list_filter = ('region', 'is_active')
    search_fields = ('name',)


@admin.register(FlyerStoreBranch)
class FlyerStoreBranchAdmin(admin.ModelAdmin):
    list_display = ('store', 'province', 'postal_code')
    list_filter = ('store', 'province')
    search_fields = ('store__name', 'province', 'postal_code')


@admin.register(FlyerCycle)
class FlyerCycleAdmin(admin.ModelAdmin):
    list_display = (
        'store',
        'province',
        'valid_from',
        'valid_to',
        'is_current',
        'scraped_at',
    )
    list_filter = ('is_current', 'store')
    search_fields = ('province',)


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
        'province',
        'cycle',
    )
    list_filter = ('store', 'valid_from', 'valid_to', 'province', 'cycle')
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
