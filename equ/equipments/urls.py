from django.urls import path
from equipments.views import QRCodeView, ReleaseEquipmentsView, CartridgeRelease

urlpatterns = [
    path('qr-code/', QRCodeView.as_view(), name='qr_code_view'),
    path('release_equipments/', ReleaseEquipmentsView.as_view(), name='release_equipments'),
    path('cartridge_release/', CartridgeRelease.as_view(), name='cartridge_release'),
]
