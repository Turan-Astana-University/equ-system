from django.urls import path, include
from django.urls import path
from . import views

urlpatterns = [
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]