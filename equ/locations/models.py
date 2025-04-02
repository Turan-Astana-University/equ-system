from django.db import models
from users.models import User
from django.apps import apps
from django.dispatch import receiver
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.conf import settings
from django.urls import reverse
# Create your models here.


class Location(models.Model):
    title = models.CharField(max_length=255)
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


@receiver(post_save, sender=Location)
def send_responsible_notification(sender, instance, created, **kwargs):
    if created and instance.responsible:
        location_url = f"{settings.SITE_URL}{reverse('location_detail', args=[instance.pk])}"
        subject = "Вы назначены ответственным за аудиторию"
        message = f"Здравствуйте, {instance.responsible.first_name}!\n\n" \
                  f"Вы были назначены ответственным за аудиторию: {instance.title}.\n\n" \
                  f"Ознакомиться можно по ссылке: {location_url}"
        recipient_list = [instance.responsible.email]

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
