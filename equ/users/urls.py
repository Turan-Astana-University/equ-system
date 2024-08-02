from django.urls import path
from .views import custom_login, index


urlpatterns = [
    path("", index, name="home"),
    path('login/', custom_login, name='login'),
]