from django.db import models

# Create your models here.


class Report(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    result_file = models.FileField(upload_to='reports/', null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)

