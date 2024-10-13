from django.urls import path
from .views import QRCodeView

urlpatterns = [
    path('qr-code/', QRCodeView.as_view(), name='qr_code_view'),
]
