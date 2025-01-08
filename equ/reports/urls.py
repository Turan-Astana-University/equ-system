from django.urls import path
from .views import EquipmentReportView, PrinterReportView, InventoryReportView
from . import views
urlpatterns = [
    path("report_equipments/", EquipmentReportView.as_view(), name="report_equipments"),
    path("report_printers/", PrinterReportView.as_view(), name="report_printers"),
    path("report_inventorys/", InventoryReportView.as_view(), name="report_inventorys"),
    path('export-excel/', views.export_excel, name='export_excel'),
]