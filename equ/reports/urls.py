from django.urls import path
from .views import get_report, get_report_printer

urlpatterns = [
    path("report/equipments", get_report, name="report_equipments"),
    path("report_printers/", get_report_printer, name="report_printers")
]