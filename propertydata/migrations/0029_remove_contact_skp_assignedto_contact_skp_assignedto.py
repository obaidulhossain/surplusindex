# Generated by Django 4.2.17 on 2025-04-04 06:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('propertydata', '0028_alter_foreclosure_surplus_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contact',
            name='skp_assignedto',
        ),
        migrations.AddField(
            model_name='contact',
            name='skp_assignedto',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assign_skp', to=settings.AUTH_USER_MODEL),
        ),
    ]
