from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Transaction

@login_required(login_url="/users/login/")
def finance_list(request):
    transactions = Transaction.objects.filter(user=request.user)
    return render(request, "finance_list.html", {"transactions": transactions})

@login_required(login_url="/users/login/")
def finance_add(request):
    if request.method == "POST":
        Transaction.objects.create(
            user=request.user,
            description=request.POST.get("description"),
            amount=request.POST.get("amount"),
            date=request.POST.get("date"),
            category=request.POST.get("category"),
            type=request.POST.get("type"),
        )
        return redirect("dashboard:home")

    return render(request, "finance_add.html")