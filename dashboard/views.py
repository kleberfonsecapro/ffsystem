import json
from datetime import date, timedelta
from calendar import month_abbr
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.http import JsonResponse
from finance.models import Transaction
from django.db.models import Sum
from django.db.models.functions import TruncMonth

@login_required(login_url="/users/login/")
def home(request):
    transactions = Transaction.objects.filter(user=request.user)
    today = date.today()

    total_income = transactions.filter(type="receita", date__lte=today).aggregate(Sum("amount"))["amount__sum"] or 0
    total_expense = transactions.filter(type="despesa", date__lte=today).aggregate(Sum("amount"))["amount__sum"] or 0
    current_balance = total_income - total_expense

    six_months_ago = date.today() - timedelta(days=180)
    monthly = (
        transactions.filter(date__gte=six_months_ago)
        .annotate(month=TruncMonth("date"))
        .values("month", "type")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )

    chart_data = {}
    for entry in monthly:
        key = entry["month"].strftime("%Y-%m")
        if key not in chart_data:
            chart_data[key] = {"income": 0, "expense": 0}
        chart_data[key][entry["type"]] = entry["total"]

    labels = []
    income_data = []
    expense_data = []
    for i in range(5, -1, -1):
        dt = date.today().replace(day=1) - timedelta(days=30 * i)
        key = dt.strftime("%Y-%m")
        labels.append(month_abbr[dt.month])
        d = chart_data.get(key, {"income": 0, "expense": 0})
        income_data.append(float(d["income"]))
        expense_data.append(float(d["expense"]))

    context = {
        "total_income": total_income,
        "total_expense": total_expense,
        "current_balance": current_balance,
        "recent_transactions": transactions.filter(date__lte=today)[:5],
        "chart_labels": json.dumps(labels),
        "chart_income": json.dumps(income_data),
        "chart_expense": json.dumps(expense_data),
    }
    return render(request, "dashboard.html", context)

@login_required(login_url="/users/login/")
def insight_api(request):
    transactions = Transaction.objects.filter(user=request.user)
    today = date.today()

    if not transactions.exists():
        return JsonResponse({"insight": "Registre algumas transações para análise."})

    total_income = transactions.filter(type="receita", date__lte=today).aggregate(Sum("amount"))["amount__sum"] or 0
    total_expense = transactions.filter(type="despesa", date__lte=today).aggregate(Sum("amount"))["amount__sum"] or 0

    if total_expense > total_income:
        insight = "Atenção: Suas despesas > receitas!"
    elif total_expense > 0:
        pct = (total_expense / total_income) * 100 if total_income > 0 else 100
        insight = f"Você gastou {pct:.1f}% das receitas."
    else:
        insight = "Sem despesas registradas!"

    return JsonResponse({"insight": insight})


@login_required(login_url="/users/login/")
def settings_view(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Senha alterada com sucesso!")
            return redirect("dashboard:settings")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "settings.html", {"form": form})
