from django.http import HttpResponseForbidden
from django.contrib import messages
from django.shortcuts import redirect
from users.models import CategoryChoicesUser


class SuperuserRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, "Доступ закрыт!")
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)


class AccountingRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        print(request.user.staff)
        if request.user.staff in [CategoryChoicesUser.ACCOUNTING, CategoryChoicesUser.ADMINISTRATION]:
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.error(request, "Доступ закрыт!")
            return redirect("home")
