# Generated by Django 5.0.7 on 2024-12-14 07:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("operations", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="operation",
            name="responsible_new",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="new_user",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="operation",
            name="responsible_old",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="old_user",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="operation",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
