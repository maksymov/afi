# Generated by Django 2.0.1 on 2018-02-02 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20180106_1715'),
    ]

    operations = [
        migrations.AddField(
            model_name='squad',
            name='lang',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
