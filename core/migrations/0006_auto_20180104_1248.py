# Generated by Django 2.0.1 on 2018-01-04 12:48

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20180104_0941'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='award',
            name='date_from',
        ),
        migrations.AddField(
            model_name='playeraward',
            name='date_from',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
