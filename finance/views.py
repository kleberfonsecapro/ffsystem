from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from .models import Transaction
from .forms import TransactionForm

@login_required(login_url="/users/login/")
def finance_list(request):
    transactions = Transaction.objects.filter(user=request.user)
    paginator = Paginator(transactions, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "finance_list.html", {"page_obj": page_obj})

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