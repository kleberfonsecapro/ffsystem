from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.views.decorators.http import require_POST

def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Conta criada com sucesso! Bem-vindo.")
            return redirect("dashboard:home")
    else:
        form = UserCreationForm()

    return render(request, "register.html", {"form": form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    if request.method == "POST":
        u = request.POST.get("username")
        p = request.POST.get("password")
        user = authenticate(request, username=u, password=p)

        if user is not None:
            auth_login(request, user)
            return redirect("dashboard:home")
        else:
            messages.error(request, "Usuário ou senha inválidos.")

    return render(request, "login.html")

@require_POST
def logout_view(request):
    auth_logout(request)
    return redirect("users:login")