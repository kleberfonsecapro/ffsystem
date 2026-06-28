from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from .models import Transaction
from .forms import TransactionForm

@login_required(login_url="/users/login/")
def finance_list(request):
    qs = Transaction.objects.filter(user=request.user).order_by("-date", "-created_at")

    months_available = (
        qs.annotate(month=TruncMonth("date"))
        .values("month")
        .distinct()
        .order_by("-month")
    )

    selected_month = request.GET.get("mes")
    if selected_month:
        qs = qs.filter(date__year=selected_month[:4], date__month=selected_month[5:7])

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
    })

@login_required(login_url="/users/login/")
def finance_add(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
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
def finance_edit(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    
    if request.method == "POST":
        form = TransactionForm(request.POST,instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, "Transação atualizada com sucesso!")
            return redirect("finance:list")
    else:
        form = TransactionForm(instance=transaction)
    return render(request, "finance_add.html", {"form":form, "editing": True})