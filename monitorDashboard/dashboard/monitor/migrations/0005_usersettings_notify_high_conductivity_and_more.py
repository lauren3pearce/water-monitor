# Generated by Django 5.2 on 2025-04-18 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0004_usersettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersettings',
            name='notify_high_conductivity',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='usersettings',
            name='notify_low_water',
            field=models.BooleanField(default=False),
        ),
    ]
