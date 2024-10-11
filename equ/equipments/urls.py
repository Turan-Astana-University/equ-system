from django.urls import path
from .views import scan_barcode, qr_code_view

urlpatterns = [
    path('scan/', scan_barcode, name='scan_barcode'),
    path('qr-code/', qr_code_view, name='qr_code_view'),
]
