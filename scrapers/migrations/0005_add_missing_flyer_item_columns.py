"""Add columns to flyer_items that were declared in the state-only 0001
migration but never applied to the pre-existing Supabase table."""

from django.db import migrations, models


def add_columns_if_missing(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'flyer_items'"
        )
        existing = {row[0] for row in cursor.fetchall()}

    FlyerItem = apps.get_model('scrapers', 'FlyerItem')
    columns_to_add = {
        'original_price': "NUMERIC(8,2)",
        'unit': "VARCHAR(50)",
        'valid_from': "DATE",
        'valid_to': "DATE",
        'image_url': "VARCHAR(200)",
        'raw_text': "TEXT",
        'flyer_page_url': "VARCHAR(200)",
        'bbox_x': "DOUBLE PRECISION",
        'bbox_y': "DOUBLE PRECISION",
        'bbox_width': "DOUBLE PRECISION",
        'bbox_height': "DOUBLE PRECISION",
        'page_width': "DOUBLE PRECISION",
        'page_height': "DOUBLE PRECISION",
    }

    with connection.cursor() as cursor:
        for col, col_type in columns_to_add.items():
            if col not in existing:
                cursor.execute(
                    f'ALTER TABLE flyer_items ADD COLUMN "{col}" {col_type} NULL'
                )


class Migration(migrations.Migration):

    dependencies = [
        ('scrapers', '0004_restore_branch_store_fk'),
    ]

    operations = [
        migrations.RunPython(add_columns_if_missing, migrations.RunPython.noop),
    ]
