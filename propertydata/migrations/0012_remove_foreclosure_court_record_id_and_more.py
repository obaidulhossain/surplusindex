# Generated by Django 4.2.17 on 2025-02-17 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('propertydata', '0011_foreclosure_surplus_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='foreclosure',
            name='court_record_id',
        ),
        migrations.AddField(
            model_name='contact',
            name='name_prefix',
            field=models.CharField(blank=True, max_length=10, verbose_name='Prefix'),
        ),
        migrations.AddField(
            model_name='contact',
            name='skiptraced',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='foreclosure',
            name='case_number',
            field=models.CharField(blank=True, max_length=255, verbose_name='Case Number'),
        ),
        migrations.AddField(
            model_name='foreclosure',
            name='case_number_ext',
            field=models.CharField(blank=True, max_length=10, verbose_name='Case Extension'),
        ),
        migrations.AddField(
            model_name='foreclosure',
            name='case_status',
            field=models.CharField(blank=True, max_length=255, verbose_name='Case Status'),
        ),
        migrations.AddField(
            model_name='foreclosure',
            name='case_type',
            field=models.CharField(blank=True, max_length=255, verbose_name='Case Type'),
        ),
        migrations.AddField(
            model_name='foreclosure',
            name='court_name',
            field=models.CharField(blank=True, max_length=255, verbose_name='Court Name'),
        ),
        migrations.AddField(
            model_name='foreclosure',
            name='defendant',
            field=models.ManyToManyField(blank=True, default='', related_name='defendant_for_foreclosure', to='propertydata.contact', verbose_name='Defendant'),
        ),
        migrations.AddField(
            model_name='foreclosure',
            name='plaintiff',
            field=models.ManyToManyField(blank=True, default='', related_name='plaintiff_for_foreclosure', to='propertydata.contact', verbose_name='Plaintiff'),
        ),
        migrations.AddField(
            model_name='foreclosure',
            name='property',
            field=models.ManyToManyField(blank=True, related_name='court_records', to='propertydata.property', verbose_name='Property'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='transaction_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='contact',
            name='name_suffix',
            field=models.CharField(blank=True, max_length=10, verbose_name='Suffix'),
        ),
        migrations.DeleteModel(
            name='Court_Record',
        ),
    ]
