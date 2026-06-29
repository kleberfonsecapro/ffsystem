from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "users"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # Desabilitado: cadastro público
    # path("register/", views.register_view, name="register"),

    # Desabilitado: recuperação de senha (exige SMTP)
    # path(
    #     "password-reset/",
    #     auth_views.PasswordResetView.as_view(
    #         template_name="registration/password_reset_form.html",
    #         email_template_name="registration/password_reset_email.html",
    #         subject_template_name="registration/password_reset_subject.txt",
    #         success_url="/users/password-reset/done/",
    #     ),
    #     name="password_reset",
    # ),
    # path(
    #     "password-reset/done/",
    #     auth_views.PasswordResetDoneView.as_view(
    #         template_name="registration/password_reset_done.html",
    #     ),
    #     name="password_reset_done",
    # ),
    # path(
    #     "password-reset/confirm/<uidb64>/<token>/",
    #     auth_views.PasswordResetConfirmView.as_view(
    #         template_name="registration/password_reset_confirm.html",
    #         success_url="/users/password-reset/complete/",
    #     ),
    #     name="password_reset_confirm",
    # ),
    # path(
    #     "password-reset/complete/",
    #     auth_views.PasswordResetCompleteView.as_view(
    #         template_name="registration/password_reset_complete.html",
    #     ),
    #     name="password_reset_complete",
    # ),
]