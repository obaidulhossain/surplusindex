# Generated by Django 4.2.17 on 2025-06-24 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('propertydata', '0051_alter_status_call_status_alter_status_lp_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='status',
            name='call_status',
            field=models.CharField(blank=True, choices=[('need_to_call', 'Need to Call'), ('responded', 'Responded'), ('not_responded', 'Not Responded'), ('re_skiptrace', 'Re Skiptrace')], default='NEED_TO_CALL', max_length=255),
        ),
        migrations.AlterField(
            model_name='status',
            name='find_contact_status',
            field=models.CharField(blank=True, choices=[('not_assigned', 'Not Assigned'), ('assigned', 'Assigned'), ('completed', 'Completed'), ('verified', 'Verified')], default='NOT_ASSIGNED', max_length=255),
        ),
        migrations.AlterField(
            model_name='status',
            name='skiptracing_status',
            field=models.CharField(blank=True, choices=[('pending', 'Pending'), ('skiptraced_found', 'Skiptraced Found'), ('skiptraced_not_found', 'Skiptraced Not Found'), ('cold_calling_located', 'Cold Calling Located'), ('cold_calling_not_located', 'Cold Calling Not Located')], default='PENDING', max_length=255),
        ),
    ]
