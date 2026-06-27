from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    path("settings/", views.settings_view, name="settings"),
    path("api/insight/", views.insight_api, name="insight"),
]