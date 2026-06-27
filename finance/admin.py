from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("description", "amount", "type", "category", "date", "user")
    list_filter = ("type", "category", "date")
    search_fields = ("description", "user__username")
