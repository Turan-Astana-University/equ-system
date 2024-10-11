from django.db import models
from users.models import User
# Create your models here.


class Location(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField()
    responsible = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    cnt = models.IntegerField(null=True, blank=True)
    # invent_code
    date_last_invent = models.DateTimeField(blank=True, null=True, verbose_name="Дата последней инвентаризации")

    def save(self, *args, **kwargs):
        # related_equipments = self.equipment_set.all()
        # self.cnt = len(related_equipments)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title}"

