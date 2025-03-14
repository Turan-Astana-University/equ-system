from django.db import models



# Create your models here.


class Department(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    location = models.ForeignKey("locations.Location", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title