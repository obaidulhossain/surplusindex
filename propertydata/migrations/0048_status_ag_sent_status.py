# Generated by Django 4.2.17 on 2025-06-17 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('propertydata', '0047_alter_status_doc_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='status',
            name='ag_sent_status',
            field=models.CharField(blank=True, choices=[('not_delivered', 'not_delivered'), ('delivered', 'delivered'), ('returned_signed', 'returned_signed'), ('returned_not_signed', 'returned_not_signed')], max_length=255),
        ),
    ]
