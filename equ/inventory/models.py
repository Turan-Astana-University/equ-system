from django.db import models
from users.models import User
from reports.models import Report
# Create your models here.


class Inventory(models.Model):
    date_start = models.DateTimeField(null=True, blank=True)
    date_end = models.DateTimeField(null=True, blank=True)
    responsible = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True, blank=True)
    report = models.ForeignKey(to=Report, on_delete=models.CASCADE, null=True, blank=True)