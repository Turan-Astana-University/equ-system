from django.urls import path, include
from django.urls import path
from .views import DashboardView, cartridge_usage_by_department

urlpatterns = [
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path("cartridge-usage/", cartridge_usage_by_department, name="cartridge_usage"),
]
