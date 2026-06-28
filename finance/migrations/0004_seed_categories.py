from django.db import migrations


DEFAULT_CATEGORIES = [
    "Salário",
    "Alimentação",
    "Transporte",
    "Lazer",
    "Moradia",
    "Saúde",
    "Educação",
    "Outros",
]


def seed_categories(apps, schema_editor):
    Category = apps.get_model("finance", "Category")
    Transaction = apps.get_model("finance", "Transaction")

    created = {}
    for name in DEFAULT_CATEGORIES:
        cat, _ = Category.objects.get_or_create(
            name=name, user=None, defaults={"type": "ambos"}
        )
        created[name] = cat

    for tx in Transaction.objects.filter(category_ref__isnull=True).iterator():
        cat = created.get(tx.category)
        if cat:
            tx.category_ref = cat
            tx.save(update_fields=["category_ref"])


class Migration(migrations.Migration):
    dependencies = [
        ("finance", "0003_category_transaction_category_ref"),
    ]

    operations = [
        migrations.RunPython(seed_categories, migrations.RunPython.noop),
    ]
