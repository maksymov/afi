# Generated by Django 2.0.1 on 2018-02-02 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_squad_lang'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='squad',
            name='lang',
        ),
        migrations.AddField(
            model_name='player',
            name='lang',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]