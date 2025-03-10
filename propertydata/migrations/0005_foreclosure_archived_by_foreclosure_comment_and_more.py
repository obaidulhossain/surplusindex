# Generated by Django 4.2.17 on 2025-01-20 09:21

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('propertydata', '0004_alter_foreclosure_sale_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='foreclosure',
            name='archived_by',
            field=models.ManyToManyField(blank=True, related_name='archived_leads', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='foreclosure',
            name='comment',
            field=models.CharField(blank=True, max_length=225),
        ),
        migrations.AddField(
            model_name='foreclosure',
            name='hidden_for',
            field=models.ManyToManyField(blank=True, related_name='hidden_leads', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='foreclosure',
            name='purchased_by',
            field=models.ManyToManyField(blank=True, related_name='purchased_leads', to=settings.AUTH_USER_MODEL),
        ),
    ]
