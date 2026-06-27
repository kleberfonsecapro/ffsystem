from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from finance.models import Transaction
from django.db.models import Sum

@login_required(login_url="/users/login/")
def home(request):
    transactions = Transaction.objects.filter(user=request.user)

    total_income = transactions.filter(type="receita").aggregate(Sum("amount"))["amount__sum"] or 0
    total_expense = transactions.filter(type="despesa").aggregate(Sum("amount"))["amount__sum"] or 0
    current_balance = total_income - total_expense

    context = {
        "total_income": total_income,
        "total_expense": total_expense,
        "current_balance": current_balance,
        "recent_transactions": transactions[:5],
    }
    return render(request, "dashboard.html", context)

@login_required(login_url="/users/login/")
def insight_api(request):
    transactions = Transaction.objects.filter(user=request.user)

    if not transactions.exists():
        return JsonResponse({"insight": "Registre algumas transações para análise."})

    total_income = sum(t.amount for t in transactions if t.type == "receita")
    total_expense = sum(t.amount for t in transactions if t.type == "despesa")

    if total_expense > total_income:
        insight = "Atenção: Suas despesas > receitas!"
    elif total_expense > 0:
        pct = (total_expense / total_income) * 100 if total_income > 0 else 100
        insight = f"Você gastou {pct:.1f}% das receitas."
    else:
        insight = "Sem despesas registradas!"

    return JsonResponse({"insight": insight})
