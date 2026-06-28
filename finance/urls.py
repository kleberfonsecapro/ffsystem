from django.urls import path
from . import views

app_name = "finance"

urlpatterns = [
    path("", views.finance_list, name="list"),
    path("delete-by-type/", views.finance_delete_by_type, name="delete_by_type"),
    path("add/", views.finance_add, name="add"),
    path("<int:pk>/delete/", views.finance_delete, name="delete"),
    path("<int:pk>/edit/", views.finance_edit, name="edit"),
    path("<int:pk>/toggle-paid/", views.finance_toggle_paid, name="toggle_paid"),
]
