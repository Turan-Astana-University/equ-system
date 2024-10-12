from django.urls import path
from .views import LoginView, index, custom_logout_view

urlpatterns = [
    path("", index, name="home"),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', custom_logout_view, name='logout'),
]