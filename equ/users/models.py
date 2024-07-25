from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from departments.models import Department
from positions.models import Position


class UserType(models.Model):
    title = models.CharField(max_length=265)


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
    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE, null=True, blank=True)
    #
    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = []
    pass