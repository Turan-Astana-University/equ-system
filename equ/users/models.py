from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from departments.models import Department
from positions.models import Position


class CategoryChoicesUser(models.TextChoices):
    ACCOUNTING = 'accounting', ('Accounting')
    ADMINISTRATION = "administration", ("Administration")


class User(AbstractUser):
    # email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_staff = models.BooleanField(default=False)
    # is_active = models.BooleanField(default=True)
    # # date_joined = models.DateTimeField(auto_now_add=True)
    #
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True, blank=True)
    staff = models.CharField(max_length=255, choices=CategoryChoicesUser.choices, null=True, blank=True)
    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.username} - {self.first_name} {self.last_name}"