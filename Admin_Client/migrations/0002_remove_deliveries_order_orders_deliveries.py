# Generated by Django 4.2.17 on 2025-04-11 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Admin_Client', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deliveries',
            name='order',
        ),
        migrations.AddField(
            model_name='orders',
            name='deliveries',
            field=models.ManyToManyField(blank=True, to='Admin_Client.deliveries'),
        ),
    ]
