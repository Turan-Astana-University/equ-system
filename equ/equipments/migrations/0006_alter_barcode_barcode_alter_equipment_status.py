# Generated by Django 5.1.4 on 2025-01-16 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipments', '0005_equipment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='barcode',
            name='barcode',
            field=models.TextField(blank=True, verbose_name='Штрих код ZPL'),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='status',
            field=models.CharField(choices=[('неисправен', 'Неисправен'), ('Новое', 'новое'), ('отремонтировано', 'Отремонтировано')], default='Новое', max_length=144),
        ),
    ]
