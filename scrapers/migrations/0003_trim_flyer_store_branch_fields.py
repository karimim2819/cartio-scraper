from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("scrapers", "0002_add_branch_cycle_and_item_fields"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="flyerstorebranch",
            name="flyer_store_latitud_f8d0e1_idx",
        ),
        migrations.RemoveField(
            model_name="flyerstorebranch",
            name="address",
        ),
        migrations.RemoveField(
            model_name="flyerstorebranch",
            name="city",
        ),
        migrations.RemoveField(
            model_name="flyerstorebranch",
            name="is_active",
        ),
        migrations.RemoveField(
            model_name="flyerstorebranch",
            name="latitude",
        ),
        migrations.RemoveField(
            model_name="flyerstorebranch",
            name="longitude",
        ),
        migrations.RemoveField(
            model_name="flyerstorebranch",
            name="store",
        ),
    ]
