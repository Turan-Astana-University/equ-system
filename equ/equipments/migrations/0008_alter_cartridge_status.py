# Generated by Django 5.0.7 on 2025-01-29 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipments', '0007_barcode_zpl_barcode_alter_barcode_barcode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartridge',
            name='status',
            field=models.CharField(choices=[('filled', 'Filled'), ('new', 'New'), ('empty', 'Empty'), ('defective', 'Defective'), ('release', 'Release')], default='new', max_length=50),
        ),
    ]
