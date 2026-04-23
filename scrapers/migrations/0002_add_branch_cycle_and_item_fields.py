# Branches, flyer cycles, and FlyerItem province/cycle link.

import django.db.models.deletion
from django.db import migrations, models


def ensure_core_flyer_tables(apps, schema_editor):
    """Create baseline tables only if missing (handles pre-seeded Supabase)."""
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        raw_names = connection.introspection.table_names(cursor)
    fold = connection.features.ignores_table_name_case
    existing = {n.casefold() for n in raw_names} if fold else set(raw_names)

    for model_name in ('FlyerStore', 'FlyerItem', 'ScrapeLog'):
        Model = apps.get_model('scrapers', model_name)
        table = Model._meta.db_table
        key = table.casefold() if fold else table
        if key not in existing:
            schema_editor.create_model(Model)
            existing.add(key)


def ensure_core_flyer_tables_reverse(apps, schema_editor):
    # Shared DB: never drop Cartio-owned / production flyer tables on reverse.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('scrapers', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(ensure_core_flyer_tables, ensure_core_flyer_tables_reverse),
        migrations.CreateModel(
            name='FlyerCycle',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                (
                    'store',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='flyer_cycles',
                        to='scrapers.flyerstore',
                    ),
                ),
                ('province', models.CharField(blank=True, max_length=50, null=True)),
                ('valid_from', models.DateField()),
                ('valid_to', models.DateField()),
                ('scraped_at', models.DateTimeField(auto_now_add=True)),
                ('is_current', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'flyer_cycles',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='FlyerStoreBranch',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                (
                    'store',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='branches',
                        to='scrapers.flyerstore',
                    ),
                ),
                ('address', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=100)),
                ('province', models.CharField(max_length=50)),
                ('postal_code', models.CharField(max_length=10)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'flyer_store_branches',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='flyeritem',
            name='province',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='flyeritem',
            name='cycle',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='flyer_items',
                to='scrapers.flyercycle',
            ),
        ),
        migrations.AddIndex(
            model_name='flyercycle',
            index=models.Index(
                fields=['store', 'is_current'],
                name='flyer_cycle_store_i_ed36d5_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='flyercycle',
            index=models.Index(
                fields=['valid_to'],
                name='flyer_cycle_valid_t_09f93c_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='flyercycle',
            index=models.Index(
                fields=['province'],
                name='flyer_cycle_provinc_54a859_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='flyerstorebranch',
            index=models.Index(
                fields=['province'],
                name='flyer_store_provinc_35b556_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='flyerstorebranch',
            index=models.Index(
                fields=['latitude', 'longitude'],
                name='flyer_store_latitud_f8d0e1_idx',
            ),
        ),
    ]
