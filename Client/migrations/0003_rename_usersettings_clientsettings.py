# Generated by Django 4.2.17 on 2025-03-10 17:43

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('realestate_directory', '0003_foreclosure_events_assigned_to_and_more'),
        ('Client', '0002_alter_usersettings_state'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserSettings',
            new_name='ClientSettings',
        ),
    ]
