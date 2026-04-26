"""Register the pre-existing normalized_name column in Django's model state.

The column already exists in the Supabase-managed flyer_items table,
so this is state-only — no DDL is executed.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrapers', '0005_add_missing_flyer_item_columns'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='flyeritem',
                    name='normalized_name',
                    field=models.CharField(max_length=255, default=''),
                    preserve_default=False,
                ),
            ],
            database_operations=[],
        ),
    ]
