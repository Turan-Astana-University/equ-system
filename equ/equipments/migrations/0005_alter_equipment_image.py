# Generated by Django 5.0.7 on 2024-07-23 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipments', '0004_equipment_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipment',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='equimages/'),
        ),
    ]
