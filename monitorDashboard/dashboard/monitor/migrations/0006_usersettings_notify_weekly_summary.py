# Generated by Django 5.2 on 2025-04-19 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0005_usersettings_notify_high_conductivity_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersettings',
            name='notify_weekly_summary',
            field=models.BooleanField(default=False),
        ),
    ]
