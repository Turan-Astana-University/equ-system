from django.urls import path
from equipments.views import QRCodeView, ReleaseEquipmentsView, CartridgeRelease, MovingEquipmentsView, MyEquipments, get_cartridges, EquipmentUpdateView

urlpatterns = [
    path('qr-code/', QRCodeView.as_view(), name='qr_code_view'),
    path('release_equipments/', ReleaseEquipmentsView.as_view(), name='release_equipments'),
    path('cartridge_release/', CartridgeRelease.as_view(), name='cartridge_release'),
    path('moving_equipments/', MovingEquipmentsView.as_view(), name='moving_equipments'),
    path('my_equipments/', MyEquipments.as_view(), name='my_equipments'),
    path('get_cartridges/', get_cartridges, name='get_cartridges'),
    path('update_equipment/', EquipmentUpdateView.as_view(), name='update_equipment'),
]
