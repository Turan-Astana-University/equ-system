# Generated by Django 5.0.7 on 2024-12-14 07:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("equipments", "0002_initial"),
        ("locations", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="cartridge",
            name="responsible",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Ответственное лицо",
            ),
        ),
        migrations.AddField(
            model_name="cartridge",
            name="cartridge_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="equipments.cartridgetypes",
                verbose_name="Тип картриджа",
            ),
        ),
        migrations.AddField(
            model_name="equipment",
            name="equipment_barcode",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="equipments.barcode",
            ),
        ),
        migrations.AddField(
            model_name="equipment",
            name="location",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="locations.location",
                verbose_name="Местонахождение",
            ),
        ),
        migrations.AddField(
            model_name="equipment",
            name="responsible",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Ответственное лицо",
            ),
        ),
        migrations.AddField(
            model_name="equipment",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="equipments.equipmenttype",
                verbose_name="Категория",
            ),
        ),
    ]
