# Generated by Django 4.2.17 on 2025-01-19 07:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('changed_at', models.DateTimeField(auto_now=True)),
                ('first_name', models.CharField(blank=True, max_length=255, verbose_name='First Name')),
                ('middle_name', models.CharField(blank=True, max_length=255, verbose_name='Middle Name')),
                ('last_name', models.CharField(blank=True, max_length=255, verbose_name='Last Name')),
                ('name_suffix', models.CharField(blank=True, max_length=255, verbose_name='Suffix')),
            ],
            options={
                'verbose_name': 'Contact',
                'verbose_name_plural': 'Contacts',
            },
        ),
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
                ('zip_code', models.CharField(blank=True, max_length=255, verbose_name='Zip')),
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
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('changed_at', models.DateTimeField(auto_now=True)),
                ('transaction_type', models.CharField(choices=[('deed', 'Deed'), ('loan', 'Loan'), ('lien', 'Lien'), ('release', 'Release')], default='Transaction Type', max_length=255, verbose_name='Transaction Type')),
                ('instrument_no', models.CharField(blank=True, max_length=255, verbose_name='Instrument No')),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=16, verbose_name='Transaction Amount')),
                ('comment', models.CharField(blank=True, max_length=255, verbose_name='Comment')),
                ('reference_transaction', models.CharField(blank=True, max_length=255, verbose_name='Reference Transaction')),
                ('first_party', models.ManyToManyField(blank=True, related_name='transactions_as_first_party', to='propertydata.contact', verbose_name='First Party - Grantor, Seller, Borrower)')),
                ('property', models.ManyToManyField(related_name='transactions_as_property', to='propertydata.property', verbose_name='Property')),
                ('second_party', models.ManyToManyField(blank=True, related_name='transactions_as_second_party', to='propertydata.contact', verbose_name='Second Party - Grantee, Buyer, Lender')),
                ('third_party', models.ManyToManyField(blank=True, related_name='transactions_as_third_party', to='propertydata.contact', verbose_name='Third Party - Trustee, Guarantor, Attorney')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Court_Record',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('changed_at', models.DateTimeField(auto_now=True)),
                ('case_number', models.CharField(blank=True, max_length=255, verbose_name='Case Number')),
                ('court_name', models.CharField(blank=True, max_length=255, verbose_name='Court Name')),
                ('case_type', models.CharField(blank=True, max_length=255, verbose_name='Case Type')),
                ('case_status', models.CharField(blank=True, max_length=255, verbose_name='Case Status')),
                ('defendant', models.ForeignKey(blank=True, default='', on_delete=django.db.models.deletion.CASCADE, related_name='court_records_as_defendant', to='propertydata.contact', verbose_name='Defendant')),
                ('plaintiff', models.ForeignKey(blank=True, default='', on_delete=django.db.models.deletion.CASCADE, related_name='court_records_as_plaintiff', to='propertydata.contact', verbose_name='Plaintiff')),
                ('property', models.ManyToManyField(blank=True, related_name='court_records', to='propertydata.property', verbose_name='Property')),
            ],
            options={
                'verbose_name': 'Court Record',
                'verbose_name_plural': 'Court Records',
            },
        ),
        migrations.AddField(
            model_name='contact',
            name='emails',
            field=models.ManyToManyField(blank=True, related_name='contact_as_email', to='propertydata.email', verbose_name='Email Addresses'),
        ),
        migrations.AddField(
            model_name='contact',
            name='landline',
            field=models.ManyToManyField(blank=True, related_name='contact_as_landline', to='propertydata.landline_number', verbose_name='Landline Numbers'),
        ),
        migrations.AddField(
            model_name='contact',
            name='mailing_address',
            field=models.ManyToManyField(blank=True, related_name='contacts_as_mailing_address', to='propertydata.property', verbose_name='Mailing Address'),
        ),
        migrations.AddField(
            model_name='contact',
            name='wireless',
            field=models.ManyToManyField(blank=True, related_name='contact_as_wireless', to='propertydata.wireless_number', verbose_name='Wireless Numbers'),
        ),
    ]
