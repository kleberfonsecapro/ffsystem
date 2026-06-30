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
    path("export-csv/", views.export_csv, name="export_csv"),
    path("import-csv/", views.import_csv, name="import_csv"),
    path("<int:pk>/upload-doc/", views.finance_upload_document, name="upload_document"),
    path("<int:pk>/delete-doc/<int:doc_id>/", views.finance_delete_document, name="delete_document"),
    path("<int:pk>/download-doc/<int:doc_id>/", views.finance_download_document, name="download_document"),
    path("installment-group/<uuid:group_id>/delete/", views.finance_delete_installment_group, name="delete_installment_group"),
    path("reports/", views.finance_reports, name="reports"),
    path("reports/pdf/", views.finance_reports_pdf, name="reports_pdf"),
    path("analysis/", views.finance_analysis, name="analysis"),
]
