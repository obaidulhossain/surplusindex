# Generated by Django 4.2.17 on 2025-02-04 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('si_user', '0013_alter_userpayment_stripe_customer_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdetail',
            name='stripe_customer_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
