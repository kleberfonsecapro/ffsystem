from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
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

    total_income = transactions.filter(type="receita").aggregate(Sum("amount"))["amount__sum"] or 0
    total_expense = transactions.filter(type="despesa").aggregate(Sum("amount"))["amount__sum"] or 0

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
