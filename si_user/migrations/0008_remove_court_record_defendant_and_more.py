# Generated by Django 4.2.17 on 2025-01-19 07:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('si_user', '0007_alter_property_zip_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='court_record',
            name='defendant',
        ),
        migrations.RemoveField(
            model_name='court_record',
            name='plaintiff',
        ),
        migrations.RemoveField(
            model_name='court_record',
            name='property',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='first_party',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='property',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='second_party',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='third_party',
        ),
        migrations.DeleteModel(
            name='Contact',
        ),
        migrations.DeleteModel(
            name='Court_Record',
        ),
        migrations.DeleteModel(
            name='Email',
        ),
        migrations.DeleteModel(
            name='Landline_Number',
        ),
        migrations.DeleteModel(
            name='Property',
        ),
        migrations.DeleteModel(
            name='Transaction',
        ),
        migrations.DeleteModel(
            name='Wireless_Number',
        ),
    ]
