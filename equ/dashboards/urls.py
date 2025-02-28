from django.urls import path, include
from django.urls import path
from .views import DashboardView

urlpatterns = [
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
