# Generated by Django 4.2.17 on 2025-04-21 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('propertydata', '0033_status_first_contact_address_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='status',
            old_name='find_contact_comment',
            new_name='find_contact_notes',
        ),
        migrations.AddField(
            model_name='status',
            name='first_contact_comment',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='status',
            name='second_contact_comment',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
