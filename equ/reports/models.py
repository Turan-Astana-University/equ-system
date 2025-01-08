from django.db import models

# Create your models here.


class CategoryChoices(models.TextChoices):
    INVENTORY = 'inventory', ('Inventory')



class Report(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    result_file = models.FileField(upload_to='reports/', null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    category_report = models.CharField(max_length=255, choices=CategoryChoices, null=True, blank=True)

    def __str__(self):
        return f"Report {self.id} - {self.title}"
