from django.db import models

# Create your models here.


class Inventory(models.Model):
    date_start = models.DateTimeField(null=True, blank=True)
    date_end = models.DateTimeField(null=True, blank=True)