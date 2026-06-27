from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
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