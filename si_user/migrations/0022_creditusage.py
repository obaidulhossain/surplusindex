# Generated by Django 4.2.17 on 2025-04-16 05:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('propertydata', '0032_alter_contact_changed_at_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('si_user', '0021_alter_userdetail_created_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreditUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('changed_at', models.DateTimeField(auto_now=True, null=True)),
                ('credits_used', models.IntegerField(blank=True, max_length=3, null=True)),
                ('number_of_free', models.IntegerField(blank=True, max_length=3, null=True)),
                ('number_of_purchased', models.IntegerField(blank=True, max_length=3, null=True)),
                ('leads', models.ManyToManyField(blank=True, to='propertydata.foreclosure')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
