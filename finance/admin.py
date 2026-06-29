from django.contrib import admin
from .models import Transaction, Category, TransactionDocument


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "type")
    list_filter = ("type",)
    search_fields = ("name",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("description", "amount", "type", "category_display", "date", "user")
    list_filter = ("type", "category_ref", "date")
    search_fields = ("description", "user__username")


@admin.register(TransactionDocument)
class TransactionDocumentAdmin(admin.ModelAdmin):
    list_display = ("filename_original", "transaction", "filesize", "uploaded_at")
    list_filter = ("uploaded_at",)
    search_fields = ("filename_original", "transaction__description")
