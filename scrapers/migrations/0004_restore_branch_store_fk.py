import django.db.models.deletion
from django.db import migrations, models


def backfill_branch_store(apps, schema_editor):
    FlyerStore = apps.get_model("scrapers", "FlyerStore")
    FlyerStoreBranch = apps.get_model("scrapers", "FlyerStoreBranch")

    null_qs = FlyerStoreBranch.objects.filter(store__isnull=True)
    if not null_qs.exists():
        return

    stores = list(FlyerStore.objects.order_by("id").values_list("id", flat=True))
    if len(stores) == 1:
        null_qs.update(store_id=stores[0])
        return

    raise RuntimeError(
        "Cannot enforce non-null store on flyer_store_branches: "
        "found rows with NULL store_id and could not infer store automatically. "
        "Please populate store_id for all existing rows, then rerun migrations."
    )


class Migration(migrations.Migration):
    dependencies = [
        ("scrapers", "0003_trim_flyer_store_branch_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="flyerstorebranch",
            name="store",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="branches",
                to="scrapers.flyerstore",
            ),
        ),
        migrations.RunPython(backfill_branch_store, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="flyerstorebranch",
            name="store",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="branches",
                to="scrapers.flyerstore",
            ),
        ),
    ]
