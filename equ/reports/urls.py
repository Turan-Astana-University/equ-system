from django.urls import path
from .views import get_report

urlpatterns = [
    path("report/", get_report, name="report"),
]