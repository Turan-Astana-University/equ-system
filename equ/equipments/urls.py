from django.urls import path
from equipments.views import QRCodeView, release_equipments

urlpatterns = [
    path('qr-code/', QRCodeView.as_view(), name='qr_code_view'),
    path('release_equipments/', release_equipments, name='release_equipments'),
]
