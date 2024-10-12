from django.shortcuts import render, redirect
from .forms import CustomLoginForm
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.urls import reverse

# Create your views here.

def custom_logout_view(request):
    logout(request)
    return redirect(reverse('login')) 

def index(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect("invent")
        return redirect('login')


class LoginView(View):
    form_class = CustomLoginForm
    template_name = 'users/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Замените на нужный URL
            else:
                form.add_error(None, 'Неверное имя пользователя или пароль.')
        return render(request, self.template_name, {'form': form})

