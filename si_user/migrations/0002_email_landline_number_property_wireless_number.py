# Generated by Django 4.2.17 on 2025-01-10 07:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('si_user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_address', models.EmailField(max_length=255, verbose_name='Email')),
                ('status', models.CharField(blank=True, max_length=255, verbose_name='Status')),
            ],
            options={
                'verbose_name': 'Email',
                'verbose_name_plural': 'Emails',
            },
        ),
        migrations.CreateModel(
            name='Landline_Number',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('l_number', models.CharField(blank=True, max_length=255, verbose_name='Landline Number')),
                ('l_caller_id', models.CharField(blank=True, max_length=255, verbose_name='Landline Caller ID')),
                ('l_status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=255, verbose_name='Status')),
            ],
            options={
                'verbose_name': 'Landline Number',
                'verbose_name_plural': 'Landline Numbers',
            },
        ),
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('changed_at', models.DateTimeField(auto_now=True)),
                ('parcel', models.CharField(blank=True, max_length=255, verbose_name='Parcel ID')),
                ('state', models.CharField(blank=True, max_length=255, verbose_name='State')),
                ('county', models.CharField(blank=True, max_length=255, verbose_name='County')),
                ('house_number', models.CharField(blank=True, max_length=255, verbose_name='House')),
                ('road_name', models.CharField(blank=True, max_length=255, verbose_name='Road')),
                ('road_type', models.CharField(blank=True, max_length=255, verbose_name='Road Type')),
                ('direction', models.CharField(blank=True, max_length=255, verbose_name='Direction')),
                ('apt_unit', models.CharField(blank=True, max_length=255, verbose_name='Apartment/Unit')),
                ('extention', models.CharField(blank=True, max_length=255, verbose_name='Extension')),
                ('city', models.CharField(blank=True, max_length=255, verbose_name='City')),
                ('zip_code', models.IntegerField(blank=True, verbose_name='Zip')),
            ],
            options={
                'verbose_name': 'Property',
                'verbose_name_plural': 'Properties',
            },
        ),
        migrations.CreateModel(
            name='Wireless_Number',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('w_number', models.CharField(blank=True, max_length=255, verbose_name='Wireless Number')),
                ('w_caller_id', models.CharField(blank=True, max_length=255, verbose_name='Wireless Caller ID')),
                ('w_status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=255, verbose_name='Status')),
            ],
            options={
                'verbose_name': 'Wireless Number',
                'verbose_name_plural': 'Wireless Numbers',
            },
        ),
    ]
