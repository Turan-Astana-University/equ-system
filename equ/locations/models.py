from django.db import models
from users.models import User
# Create your models here.


class Location(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField()
    responsible = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    # invent_code

    def __str__(self):
        return f"{self.title}"