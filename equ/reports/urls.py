from django.urls import path
from .views import get_report, get_report_printer

urlpatterns = [
    path("report/", get_report, name="report"),
    path("report_printers/", get_report_printer, name="report_printers")
]