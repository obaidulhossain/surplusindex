# Generated by Django 4.2.17 on 2025-04-12 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Admin_Client', '0003_orders_order_price_orders_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliveries',
            name='delivred_in',
            field=models.DateField(blank=True, null=True),
        ),
    ]
