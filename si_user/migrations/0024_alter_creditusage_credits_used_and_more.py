# Generated by Django 4.2.17 on 2025-04-17 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('si_user', '0023_alter_creditusage_leads'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditusage',
            name='credits_used',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='creditusage',
            name='number_of_free',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='creditusage',
            name='number_of_purchased',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userdetail',
            name='phone',
            field=models.CharField(blank=True, max_length=13),
        ),
    ]
