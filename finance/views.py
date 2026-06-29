import csv
import io
import uuid
from datetime import datetime
import json
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.template.loader import render_to_string
from weasyprint import HTML
from dateutil.relativedelta import relativedelta
from .models import Transaction, Category, TransactionDocument
from .forms import TransactionForm, CSVImportForm, TransactionDocumentForm
from .categories import resolve_category


def apply_transaction_filters(qs, request):
    selected_month = request.GET.get("mes")
    if selected_month:
        qs = qs.filter(date__year=selected_month[:4], date__month=selected_month[5:7])

    selected_type = request.GET.get("tipo")
    if selected_type:
        if selected_type == "despesa_parcelada":
            qs = qs.filter(type="despesa", is_installment=True)
        else:
            qs = qs.filter(type=selected_type)

    selected_category = request.GET.get("categoria")
    if selected_category:
        qs = qs.filter(category_ref__name=selected_category)

    return qs


def format_brazilian_currency(value):
    formatted = f"{value:,.2f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


@login_required(login_url="/users/login/")
def finance_list(request):
    qs_base = Transaction.objects.filter(user=request.user).prefetch_related("documents").order_by("-date", "-created_at")

    months_available = (
        qs_base.annotate(month=TruncMonth("date"))
        .values("month")
        .distinct()
        .order_by("-month")
    )

    qs = apply_transaction_filters(qs_base, request)

    selected_month = request.GET.get("mes")
    selected_type = request.GET.get("tipo")
    selected_category = request.GET.get("categoria")

    categories_available = Category.objects.filter(
        user__in=[None, request.user]
    ).values_list("name", flat=True).distinct().order_by("name")

    # Type choices for filter - add "despesa_parcelada" option
    type_choices = list(Transaction.TYPE_CHOICES) + [("despesa_parcelada", "Despesa Parcelada")]

    # Special handling for "despesa_parcelada" filter - group by installment_group
    if selected_type == "despesa_parcelada":
        # Backfill installment_group for orphaned installment transactions
        orphans = qs.filter(installment_group__isnull=True)
        if orphans.exists():
            group_map = {}
            for tx in orphans:
                key = (tx.description, tx.installment_total)
                if key not in group_map:
                    group_map[key] = uuid.uuid4()
            for tx in orphans:
                key = (tx.description, tx.installment_total)
                Transaction.objects.filter(pk=tx.pk).update(installment_group=group_map[key])

        # Group by installment_group
        installment_groups = {}
        for tx in qs:
            group_id = tx.installment_group
            if group_id not in installment_groups:
                installment_groups[group_id] = {
                    "group_id": group_id,
                    "description": tx.description,
                    "category": tx.category_display,
                    "total_amount": 0,
                    "installment_total": tx.installment_total,
                    "installments": [],
                    "first_date": tx.date,
                    "last_date": tx.date,
                }
            installment_groups[group_id]["installments"].append(tx)
            installment_groups[group_id]["total_amount"] += tx.amount
            if tx.date < installment_groups[group_id]["first_date"]:
                installment_groups[group_id]["first_date"] = tx.date
            if tx.date > installment_groups[group_id]["last_date"]:
                installment_groups[group_id]["last_date"] = tx.date

        # Convert to list and sort by first_date desc
        grouped = list(installment_groups.values())
        grouped.sort(key=lambda g: g["first_date"], reverse=True)

        # Calculate subtotals for template compatibility
        for g in grouped:
            g["income"] = 0
            g["expense"] = g["total_amount"]
            g["month"] = g["first_date"]  # for template compatibility
    else:
        # Normal monthly grouping
        grouped = []
        current_month = None
        for tx in qs:
            key = tx.date.strftime("%Y-%m")
            if key != current_month:
                current_month = key
                grouped.append({"month": tx.date, "transactions": [], "income": 0, "expense": 0})
            grouped[-1]["transactions"].append(tx)
            if tx.type == "receita":
                grouped[-1]["income"] += tx.amount
            else:
                grouped[-1]["expense"] += tx.amount

    return render(request, "finance_list.html", {
        "grouped_transactions": grouped,
        "months_available": [m["month"] for m in months_available],
        "selected_month": selected_month,
        "selected_type": selected_type,
        "selected_category": selected_category,
        "categories_available": categories_available,
        "type_choices": type_choices,
        "import_form": CSVImportForm(),
    })


@login_required(login_url="/users/login/")
def export_csv(request):
    qs = apply_transaction_filters(
        Transaction.objects.filter(user=request.user).order_by("-date", "-created_at"),
        request,
    )

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = "attachment; filename=transacoes.csv"
    response.write("\ufeff")

    writer = csv.writer(response, delimiter=";", lineterminator="\r\n")
    writer.writerow(["Data", "Descrição", "Categoria", "Tipo", "Valor", "Parcela", "Paga"])

    for tx in qs:
        installment = ""
        if tx.is_installment and tx.installment_number and tx.installment_total:
            installment = f"{tx.installment_number}/{tx.installment_total}"

        writer.writerow([
            tx.date.strftime("%d/%m/%Y"),
            tx.description,
            tx.category_display,
            tx.type,
            format_brazilian_currency(tx.amount),
            installment,
            "Sim" if tx.paid else "Não",
        ])

    return response


@login_required(login_url="/users/login/")
@require_POST
def import_csv(request):
    form = CSVImportForm(request.POST, request.FILES)
    if not form.is_valid():
        for errors in form.errors.values():
            for error in errors:
                messages.error(request, error)
        return redirect("finance:list")

    csv_file = form.cleaned_data["file"]
    csv_file.seek(0)
    text_file = io.TextIOWrapper(csv_file, encoding="utf-8-sig", newline="")
    reader = csv.DictReader(text_file, delimiter=";")
    required_fields = ["Data", "Descrição", "Categoria", "Tipo", "Valor", "Parcela", "Paga"]

    if not reader.fieldnames or any(field not in reader.fieldnames for field in required_fields):
        messages.error(request, "Cabeçalho inválido. Use: Data;Descrição;Categoria;Tipo;Valor;Parcela;Paga")
        return redirect("finance:list")

    success_count = 0
    error_count = 0
    line_number = 2
    import_group_map = {}

    for row in reader:
        errors = []
        raw_date = (row.get("Data") or "").strip()
        raw_description = (row.get("Descrição") or "").strip()
        raw_category = (row.get("Categoria") or "").strip()
        raw_type = (row.get("Tipo") or "").strip().lower()
        raw_amount = (row.get("Valor") or "").strip()
        raw_parcela = (row.get("Parcela") or "").strip()
        raw_paid = (row.get("Paga") or "").strip().lower()

        if not raw_date:
            errors.append("Data obrigatória.")
        if not raw_description:
            errors.append("Descrição obrigatória.")
        if not raw_category:
            errors.append("Categoria obrigatória.")
        if raw_type not in ["receita", "despesa"]:
            errors.append("Tipo deve ser 'receita' ou 'despesa'.")
        if not raw_amount:
            errors.append("Valor obrigatório.")

        date_value = None
        if raw_date:
            try:
                if "/" in raw_date:
                    date_value = datetime.strptime(raw_date, "%d/%m/%Y").date()
                else:
                    date_value = datetime.strptime(raw_date, "%Y-%m-%d").date()
            except ValueError:
                errors.append("Data inválida. Use dd/mm/AAAA ou aaaa-mm-dd.")

        amount_value = None
        if raw_amount:
            normalized_amount = raw_amount.replace(".", "").replace(",", ".")
            try:
                amount_value = Decimal(normalized_amount)
                if amount_value <= 0:
                    errors.append("O valor deve ser maior que zero.")
            except (InvalidOperation, ValueError):
                errors.append("Valor inválido. Use formato 1.234,56 ou 1234.56.")

        paid_value = False
        if raw_paid:
            if raw_paid in ["sim", "s", "true", "1", "yes"]:
                paid_value = True
            elif raw_paid in ["não", "nao", "n", "false", "0", "no"]:
                paid_value = False
            else:
                errors.append("Valor de 'Paga' inválido. Use Sim ou Não.")

        is_installment = False
        installment_number = None
        installment_total = None
        installment_group = None
        if raw_parcela:
            parts = [p.strip() for p in raw_parcela.split("/") if p.strip()]
            if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
                errors.append("Parcela inválida. Use formato 1/12.")
            else:
                installment_number = int(parts[0])
                installment_total = int(parts[1])
                if installment_number < 1 or installment_total < 1 or installment_number > installment_total:
                    errors.append("Parcela inválida. O número da parcela deve ser entre 1 e total.")
                else:
                    is_installment = True
                    group_key = (raw_description, installment_total)
                    if group_key not in import_group_map:
                        import_group_map[group_key] = uuid.uuid4()
                    installment_group = import_group_map[group_key]

        if errors:
            for error in errors:
                messages.error(request, f"Linha {line_number}: {error}")
            error_count += 1
            line_number += 1
            continue

        category_ref = resolve_category(request.user, raw_category, raw_type)

        Transaction.objects.create(
            user=request.user,
            description=raw_description,
            amount=amount_value,
            date=date_value,
            category_ref=category_ref,
            type=raw_type,
            paid=paid_value,
            is_installment=is_installment,
            installment_number=installment_number,
            installment_total=installment_total,
            installment_group=installment_group,
        )
        success_count += 1
        line_number += 1

    text_file.close()

    if success_count > 0:
        messages.success(request, f"{success_count} transação(ões) importada(s) com sucesso.")
    if error_count > 0:
        messages.error(request, f"{error_count} linha(s) com erro foram ignoradas.")

    return redirect("finance:list")


@login_required(login_url="/users/login/")
def finance_add(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            is_installment = form.cleaned_data.get("is_installment")
            if is_installment:
                total = form.cleaned_data["installment_total"]
                total_amount = form.cleaned_data["amount"]
                first_date = form.cleaned_data["date"]
                group_id = uuid.uuid4()
                total_cents = int(round(total_amount * 100))
                base_cents = total_cents // total
                remainder = total_cents % total

                for i in range(1, total + 1):
                    parcel_cents = base_cents + (1 if i <= remainder else 0)
                    parcel_amount = Decimal(parcel_cents) / Decimal(100)
                    Transaction.objects.create(
                        user=request.user,
                        description=form.cleaned_data["description"],
                        amount=parcel_amount,
                        date=first_date + relativedelta(months=i - 1),
                        category_ref=form.cleaned_data["category_ref"],
                        type=form.cleaned_data["type"],
                        is_installment=True,
                        installment_total=total,
                        installment_number=i,
                        installment_group=group_id,
                    )

                messages.success(request, f"Compra parcelada em {total}x registrada!")
                return redirect("dashboard:home")
            else:
                transaction = form.save(commit=False)
                transaction.user = request.user
                transaction.save()
                messages.success(request, "Transação registrada com sucesso!")
                return redirect("dashboard:home")
        else:
            messages.error(request, "Erro nos dados informados. Verifique e tente novamente.")
    else:
        form = TransactionForm()

    return render(request, "finance_add.html", {"form": form})


@login_required(login_url="/users/login/")
@require_POST
def finance_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    transaction.delete()
    messages.success(request, "Transação excluída com sucesso!")
    return redirect("finance:list")


@login_required(login_url="/users/login/")
@require_POST
def finance_delete_by_type(request):
    selected_type = request.POST.get("tipo")
    if selected_type not in ["receita", "despesa"]:
        messages.error(request, "Tipo inválido para exclusão em massa.")
        return redirect("finance:list")

    transactions = Transaction.objects.filter(user=request.user, type=selected_type)
    count = transactions.count()
    if count == 0:
        messages.info(request, f"Nenhuma transação do tipo {selected_type} foi encontrada.")
    else:
        transactions.delete()
        label = "receitas" if selected_type == "receita" else "despesas"
        messages.success(request, f"{count} {label} excluída(s) com sucesso!")

    return redirect("finance:list")


@login_required(login_url="/users/login/")
@require_POST
def finance_toggle_paid(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    transaction.paid = not transaction.paid
    transaction.save()
    status = "paga" if transaction.paid else "não paga"
    messages.success(request, f"Transação marcada como {status}!")
    return redirect("finance:list")


@login_required(login_url="/users/login/")
@require_POST
def finance_delete_installment_group(request, group_id):
    """Deleta todas as parcelas de um grupo de parcelamento."""
    transactions = Transaction.objects.filter(user=request.user, installment_group=group_id)
    count = transactions.count()
    if count == 0:
        messages.info(request, "Nenhuma parcela encontrada para este grupo.")
    else:
        first_tx = transactions.first()
        desc = first_tx.description
        transactions.delete()
        messages.success(request, f"Grupo de parcelas \"{desc}\" ({count} parcelas) excluído com sucesso!")
    return redirect("finance:list")


@login_required(login_url="/users/login/")
@require_POST
def finance_upload_document(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    form = TransactionDocumentForm(request.POST, request.FILES)
    if form.is_valid():
        doc = form.save(commit=False)
        doc.transaction = transaction
        doc.filename_original = form.cleaned_data["file"].name
        doc.filesize = form.cleaned_data["file"].size
        doc.save()
        messages.success(request, f"Comprovante \"{doc.filename_original}\" anexado com sucesso!")
    else:
        for errors in form.errors.values():
            for error in errors:
                messages.error(request, error)
    return redirect("finance:list")


@login_required(login_url="/users/login/")
@require_POST
def finance_delete_document(request, pk, doc_id):
    doc = get_object_or_404(TransactionDocument, pk=doc_id, transaction__pk=pk, transaction__user=request.user)
    filename = doc.filename_original
    doc.file.delete()
    doc.delete()
    messages.success(request, f"Comprovante \"{filename}\" removido com sucesso!")
    return redirect("finance:list")


@login_required(login_url="/users/login/")
def finance_edit(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    if request.method == "POST":
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, "Transação atualizada com sucesso!")
            return redirect("finance:list")
    else:
        form = TransactionForm(instance=transaction)
    return render(request, "finance_add.html", {"form": form, "editing": True})


@login_required(login_url="/users/login/")
def finance_reports(request):
    """Relatório comparativo entre meses."""
    user_transactions = Transaction.objects.filter(user=request.user)
    months_available = (
        user_transactions
        .dates("date", "month", order="DESC")
    )

    selected_months = request.GET.getlist("meses")

    months_data = []
    all_categories = set()

    for month_str in selected_months:
        try:
            year, month = int(month_str[:4]), int(month_str[5:7])
        except (ValueError, IndexError):
            continue
        qs = user_transactions.filter(date__year=year, date__month=month)
        income = qs.filter(type="receita").aggregate(t=Sum("amount"))["t"] or 0
        expense = qs.filter(type="despesa").aggregate(t=Sum("amount"))["t"] or 0
        cats = {}
        for tx in qs:
            cat_name = tx.category_display
            all_categories.add(cat_name)
            cats.setdefault(cat_name, {"income": 0, "expense": 0})
            if tx.type == "receita":
                cats[cat_name]["income"] += tx.amount
            else:
                cats[cat_name]["expense"] += tx.amount
        months_data.append({
            "month_str": f"{month:02d}/{year}",
            "income": income,
            "expense": expense,
            "balance": income - expense,
            "categories": cats,
        })

    category_rows = []
    for cat in sorted(all_categories):
        row = {"category": cat}
        for md in months_data:
            row[md["month_str"]] = md["categories"].get(cat, {"income": 0, "expense": 0})
        category_rows.append(row)

    context = {
        "months_available": months_available,
        "selected_months": selected_months,
        "months_data": months_data,
        "category_rows": category_rows,
    }
    return render(request, "finance_reports.html", context)


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


@login_required(login_url="/users/login/")
def finance_analysis(request):
    """Painel analítico — dados serializados para renderização client-side."""
    user_transactions = Transaction.objects.filter(user=request.user)

    months_qs = user_transactions.dates("date", "month", order="ASC")

    # Mapear mês/ano para label curta
    month_map = {}
    for dt in months_qs:
        key = dt.strftime("%Y-%m")
        label = dt.strftime("%b").capitalize()
        month_map[key] = label

    all_month_keys = sorted(month_map.keys())

    # Construir budget_data flat (mesmo formato do código de referência)
    budget_data = []
    categories_set = set()

    for tx in user_transactions.select_related("category_ref"):
        key = tx.date.strftime("%Y-%m")
        if key not in month_map:
            continue
        label = month_map[key]
        cat_name = tx.category_display
        categories_set.add(cat_name)
        tipo = "income" if tx.type == "receita" else "expense"
        budget_data.append({
            "month": label,
            "month_key": key,
            "category": cat_name,
            "type": tipo,
            "value": float(tx.amount),
        })

    categories_list = sorted(categories_set)

    context = {
        "budget_data_json": json.dumps(budget_data, cls=DecimalEncoder),
        "months_json": json.dumps(all_month_keys),
        "month_labels_json": json.dumps([month_map[k] for k in all_month_keys]),
        "categories_json": json.dumps(categories_list),
    }
    return render(request, "finance_analysis.html", context)


@login_required(login_url="/users/login/")
def finance_reports_pdf(request):
    """Gera PDF do relatório comparativo usando WeasyPrint."""
    user_transactions = Transaction.objects.filter(user=request.user)

    selected_months = request.GET.getlist("meses")
    if not selected_months:
        latest = user_transactions.dates("date", "month", order="DESC").first()
        if latest:
            selected_months = [latest.strftime("%Y-%m")]

    months_data = []
    all_categories = set()

    for month_str in selected_months:
        try:
            year, month = int(month_str[:4]), int(month_str[5:7])
        except (ValueError, IndexError):
            continue
        qs = user_transactions.filter(date__year=year, date__month=month)
        income = qs.filter(type="receita").aggregate(t=Sum("amount"))["t"] or 0
        expense = qs.filter(type="despesa").aggregate(t=Sum("amount"))["t"] or 0
        cats = {}
        for tx in qs:
            cat_name = tx.category_display
            all_categories.add(cat_name)
            cats.setdefault(cat_name, {"income": 0, "expense": 0})
            if tx.type == "receita":
                cats[cat_name]["income"] += tx.amount
            else:
                cats[cat_name]["expense"] += tx.amount
        months_data.append({
            "month_str": f"{month:02d}/{year}",
            "income": income,
            "expense": expense,
            "balance": income - expense,
            "categories": cats,
        })

    category_rows = []
    for cat in sorted(all_categories):
        row = {"category": cat}
        for md in months_data:
            row[md["month_str"]] = md["categories"].get(cat, {"income": 0, "expense": 0})
        category_rows.append(row)

    html_string = render_to_string("finance_reports_pdf.html", {
        "months_data": months_data,
        "category_rows": category_rows,
        "selected_months": selected_months,
        "username": request.user.username,
    })

    pdf = HTML(string=html_string, base_url=request.build_absolute_uri("/")).write_pdf()

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="relatorio_financeiro.pdf"'
    return response
