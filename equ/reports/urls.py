from django.urls import path
from .views import EquipmentReportView, PrinterReportView, InventoryReportView, EquipmentDetailView, InventoryDetailView, CartridgeReportView, PackagePrint

urlpatterns = [
    path("report_equipments/", EquipmentReportView.as_view(), name="report_equipments"),
    path("report_printers/", PrinterReportView.as_view(), name="report_printers"),
    path("report_inventorys/", InventoryReportView.as_view(), name="report_inventorys"),
    path("report_equipment_detail/<int:pk>/", EquipmentDetailView.as_view(), name="equipment_detail"),
    path("report_inventory_detail/<int:pk>", InventoryDetailView.as_view(), name="inventory_detail"),
    path("report_cartridge/", CartridgeReportView.as_view(), name="report_cartridge"),
    path("package_print/", PackagePrint.as_view(), name="package_print"),
]