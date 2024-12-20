from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render

from users.models import CategoryChoicesUser


class AccountingUserRequiredMixin(UserPassesTestMixin):
    """
    Миксин для проверки, что пользователь принадлежит категории ACCOUNTING.
    """
    def test_func(self):
        # Проверяем, что у пользователя есть атрибут `staff` и он равен `CategoryChoicesUser.ACCOUNTING`
        return hasattr(self.request.user, 'staff') and self.request.user.staff in [CategoryChoicesUser.ACCOUNTING, CategoryChoicesUser.ADMINISTRATION]

    def handle_no_permission(self):
        # Обрабатываем случай, если проверка не прошла
        return render(self.request, '404.html', {'error_message': "У вас нет доступа к этому ресурсу."})
