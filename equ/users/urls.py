from django.urls import path
from .views import LoginView, index


urlpatterns = [
    path("", index, name="home"),
    path('login/', LoginView.as_view(), name='login'),
]