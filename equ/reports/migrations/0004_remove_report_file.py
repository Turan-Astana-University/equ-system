# Generated by Django 5.0.7 on 2024-12-19 10:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0003_report_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='report',
            name='file',
        ),
    ]
