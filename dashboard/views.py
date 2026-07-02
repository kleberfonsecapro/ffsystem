import json
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

MESES_PT = [
    "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]
MESES_PT_ABBR = [
    "", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
    "Jul", "Ago", "Set", "Out", "Nov", "Dez",
]
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from users.forms import AlterarSenhaForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.http import JsonResponse
from finance.models import Transaction
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from intelligence.insight import generate_insight

@login_required(login_url="/users/login/")
def home(request):
    transactions = Transaction.objects.filter(user=request.user)
    today = date.today()

    month_start = today.replace(day=1)
    month_income = transactions.filter(type="receita", date__gte=month_start, date__lte=today).aggregate(Sum("amount"))["amount__sum"] or 0
    month_expense = transactions.filter(type="despesa", date__gte=month_start, date__lte=today).aggregate(Sum("amount"))["amount__sum"] or 0
    current_balance = month_income - month_expense

    next_month_start = month_start + relativedelta(months=1)
    next_month_end = next_month_start + relativedelta(months=1) - timedelta(days=1)
    next_income = transactions.filter(type="receita", date__gte=next_month_start, date__lte=next_month_end).aggregate(Sum("amount"))["amount__sum"] or 0
    next_expense = transactions.filter(type="despesa", date__gte=next_month_start, date__lte=next_month_end).aggregate(Sum("amount"))["amount__sum"] or 0
    next_month_name = MESES_PT[next_month_start.month]

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
        labels.append(MESES_PT_ABBR[dt.month])
        d = chart_data.get(key, {"income": 0, "expense": 0})
        income_data.append(float(d["income"]))
        expense_data.append(float(d["expense"]))

    context = {
        "total_income": month_income,
        "total_expense": month_expense,
        "current_balance": current_balance,
        "next_income": next_income,
        "next_expense": next_expense,
        "next_month_name": next_month_name,
        "recent_transactions": transactions[:5],
        "chart_labels": json.dumps(labels),
        "chart_income": json.dumps(income_data),
        "chart_expense": json.dumps(expense_data),
    }
    return render(request, "dashboard.html", context)

@login_required(login_url="/users/login/")
def insight_api(request):
    insight = generate_insight(request.user)
    return JsonResponse({"insight": insight})


@login_required(login_url="/users/login/")
def settings_view(request):
    if request.method == "POST":
        form = AlterarSenhaForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Senha alterada com sucesso!")
            return redirect("dashboard:settings")
    else:
        form = AlterarSenhaForm(request.user)

    return render(request, "settings.html", {"form": form})
