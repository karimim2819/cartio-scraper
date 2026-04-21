# Baseline model state only — no DDL. Core tables are created in 0002 when missing
# (see ensure_core_flyer_tables) so pre-existing Supabase tables never hit DuplicateTable.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='FlyerStore',
                    fields=[
                        ('id', models.BigAutoField(primary_key=True, serialize=False)),
                        ('name', models.CharField(max_length=100)),
                        (
                            'region',
                            models.CharField(
                                choices=[('CA', 'Canada'), ('US', 'United States')],
                                max_length=10,
                            ),
                        ),
                        ('flyer_url', models.URLField()),
                        ('is_active', models.BooleanField(default=True)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                    ],
                    options={
                        'db_table': 'flyer_stores',
                        'managed': True,
                    },
                ),
                migrations.CreateModel(
                    name='FlyerItem',
                    fields=[
                        ('id', models.BigAutoField(primary_key=True, serialize=False)),
                        (
                            'store',
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.PROTECT,
                                related_name='items',
                                to='scrapers.flyerstore',
                            ),
                        ),
                        ('name', models.CharField(max_length=255)),
                        (
                            'price',
                            models.DecimalField(
                                decimal_places=2, max_digits=8, null=True,
                            ),
                        ),
                        (
                            'original_price',
                            models.DecimalField(
                                blank=True, decimal_places=2, max_digits=8, null=True,
                            ),
                        ),
                        ('unit', models.CharField(blank=True, max_length=50, null=True)),
                        ('valid_from', models.DateField(blank=True, null=True)),
                        ('valid_to', models.DateField(blank=True, null=True)),
                        ('image_url', models.URLField(blank=True, null=True)),
                        ('raw_text', models.TextField(blank=True, null=True)),
                        ('scraped_at', models.DateTimeField(auto_now_add=True)),
                        ('flyer_page_url', models.URLField(blank=True, null=True)),
                        ('bbox_x', models.FloatField(blank=True, null=True)),
                        ('bbox_y', models.FloatField(blank=True, null=True)),
                        ('bbox_width', models.FloatField(blank=True, null=True)),
                        ('bbox_height', models.FloatField(blank=True, null=True)),
                        ('page_width', models.FloatField(blank=True, null=True)),
                        ('page_height', models.FloatField(blank=True, null=True)),
                    ],
                    options={
                        'db_table': 'flyer_items',
                        'managed': True,
                    },
                ),
                migrations.CreateModel(
                    name='ScrapeLog',
                    fields=[
                        ('id', models.BigAutoField(primary_key=True, serialize=False)),
                        (
                            'store',
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name='scrape_logs',
                                to='scrapers.flyerstore',
                            ),
                        ),
                        ('started_at', models.DateTimeField()),
                        ('finished_at', models.DateTimeField(blank=True, null=True)),
                        ('items_scraped', models.IntegerField(default=0)),
                        (
                            'status',
                            models.CharField(
                                choices=[
                                    ('running', 'Running'),
                                    ('success', 'Success'),
                                    ('failed', 'Failed'),
                                ],
                                max_length=20,
                            ),
                        ),
                        ('error_message', models.TextField(blank=True, null=True)),
                    ],
                    options={
                        'db_table': 'flyer_scrape_logs',
                        'managed': True,
                    },
                ),
            ],
            database_operations=[],
        ),
    ]
