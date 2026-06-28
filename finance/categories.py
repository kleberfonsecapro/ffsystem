from .models import Category


def resolve_category(user, name, tx_type=None):
    """Resolve categoria por nome: global, do usuário ou nova categoria personalizada."""
    name = (name or "").strip()
    if not name:
        return None

    category = Category.objects.filter(name__iexact=name, user=user).first()
    if category:
        return category

    category = Category.objects.filter(name__iexact=name, user__isnull=True).first()
    if category:
        return category

    type_default = tx_type if tx_type in ("receita", "despesa") else "ambos"
    return Category.objects.create(name=name, user=user, type=type_default)


def default_category_names():
    return list(
        Category.objects.filter(user__isnull=True)
        .order_by("name")
        .values_list("name", flat=True)
    )
