# Generated by Django 4.2.17 on 2024-12-30 01:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='foreclosure',
            fields=[
                ('fcl_id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('state', models.CharField(max_length=225)),
                ('county', models.CharField(max_length=225)),
                ('case_no', models.CharField(max_length=225)),
                ('sale_date', models.DateField()),
                ('sale_type', models.CharField(max_length=225)),
                ('sale_status', models.CharField(max_length=225)),
                ('foreclosing_entity', models.CharField(max_length=225)),
                ('defendant', models.CharField(max_length=225)),
                ('additional_party_1', models.CharField(max_length=225)),
                ('additional_party_2', models.CharField(max_length=225)),
                ('additional_party_3', models.CharField(max_length=225)),
                ('additional_party_4', models.CharField(max_length=225)),
                ('additional_party_5', models.CharField(max_length=225)),
                ('fcl_final_judgment', models.DecimalField(decimal_places=2, max_digits=10)),
                ('sale_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('possible_surplus', models.DecimalField(decimal_places=2, max_digits=10)),
                ('verified_surplus', models.DecimalField(decimal_places=2, max_digits=10)),
                ('si_date_listed', models.DateField()),
                ('si_last_updated', models.DateField()),
                ('si_next_update', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monthly_free_credit', models.IntegerField(default=20)),
                ('purchased_credit_balance', models.IntegerField(default=0)),
                ('pay_as_you_go', models.BooleanField(default=False)),
                ('user_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
