from django.urls import path
from .views import EquipmentReportView, PrinterReportView, InventoryReportView, EquipmentDetailView

urlpatterns = [
    path("report_equipments/", EquipmentReportView.as_view(), name="report_equipments"),
    path("report_printers/", PrinterReportView.as_view(), name="report_printers"),
    path("report_inventorys/", InventoryReportView.as_view(), name="report_inventorys"),
    path("report_equipment_detail/<int:pk>/", EquipmentDetailView.as_view(), name="equipment_detail")
]