from django.db import models

# Create your models here.


class CategoryChoices(models.TextChoices):
    INVENTORY = 'inventory', ('Inventory')


class Report(models.Model):
    title = models.CharField(max_length=255)
    result_file = models.FileField(upload_to='reports/')
    date = models.DateTimeField()
    category_report = models.CharField(max_length=255, choices=CategoryChoices)

    def __str__(self):
        return f"Report {self.id} - {self.title}"
