from django.db import models
from django.contrib.auth.models import User

# ----- CHOICES FOR GLOBAL USE -------------------------------- # 
ACTIVE = 'active'                                               # 
INACTIVE = 'inactive'                                           # 
STATUSCHOICES = (                                               # 
    (ACTIVE, 'Active'),                                         # 
    (INACTIVE, 'Inactive')                                      # 
    )                                                           # 
# ----- CHOICES FOR GLOBAL USE -------------------------------- # 

# ------------------------------------------------------------- #

# ----- ABSTRACT CLASS TO BE USED IN OTHER MODELS ------------- # 
class OperationStat(models.Model):                              #
    created_at = models.DateTimeField(auto_now_add=True)        #
    changed_at = models.DateTimeField(auto_now=True)            #
    class Meta:                                                 #
        abstract = True                                         #
# ----- ABSTRACT CLASS TO BE USED IN OTHER MODELS ------------- #
 
# ------------------------------------------------------------- #

class Property(OperationStat):
    parcel = models.CharField(max_length=255, blank=True, verbose_name='Parcel ID')
    state = models.CharField(max_length=255, blank=True, verbose_name='State')
    county = models.CharField(max_length=255, blank=True, verbose_name='County')
    house_number = models.CharField(max_length=255, blank=True, verbose_name='House')
    road_name = models.CharField(max_length=255, blank=True, verbose_name='Road')
    road_type = models.CharField(max_length=255, blank=True, verbose_name='Road Type')
    direction = models.CharField(max_length=255, blank=True, verbose_name='Direction')
    apt_unit = models.CharField(max_length=255, blank=True, verbose_name='Apartment/Unit')
    extention = models.CharField(max_length=255, blank=True, verbose_name='Extension')
    city = models.CharField(max_length=255, blank=True, verbose_name='City')
    zip_code = models.CharField(max_length=255, blank=True, verbose_name='Zip')

    class Meta:
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'

    @property
    def fulladdress (self):
        return f"{self.house_number} {self.road_name} {self.road_type} {self.direction} {self.apt_unit} {self.extention} | {self.city}, {self.zip_code}"

# ------------------------------------------------------------- #

class Email(models.Model):
    email_address = models.EmailField(max_length=255, verbose_name = "Email")
    status = models.CharField(max_length=255, blank=True, verbose_name='Status')
    
#    def __str__(self):
#        return self.email_address
    
    class Meta:
        verbose_name = "Email"
        verbose_name_plural = "Emails"
    
# ------------------------------------------------------------- #

class Wireless_Number(models.Model):
    w_number = models.CharField(max_length=255, blank=True, verbose_name='Wireless Number')
    w_caller_id = models.CharField(max_length=255, blank=True, verbose_name='Wireless Caller ID')
    w_status = models.CharField(max_length=255, choices=STATUSCHOICES, default=ACTIVE, verbose_name='Status')

    class Meta:
        verbose_name = 'Wireless Number'
        verbose_name_plural = 'Wireless Numbers'
    
    def __str__(self):
        return self.email_address

# ------------------------------------------------------------- #

class Landline_Number(models.Model):
    l_number = models.CharField(max_length=255, blank=True, verbose_name='Landline Number')
    l_caller_id = models.CharField(max_length=255, blank=True, verbose_name='Landline Caller ID')
    l_status = models.CharField(max_length=255, choices=STATUSCHOICES, default=ACTIVE, verbose_name='Status')

    class Meta:
        verbose_name = 'Landline Number'
        verbose_name_plural = 'Landline Numbers'

# ------------------------------------------------------------- #
# ------------------------------------------------------------- #

class Contact(OperationStat):
    first_name = models.CharField(max_length=255, blank=True, verbose_name='First Name')
    middle_name = models.CharField(max_length=255, blank=True, verbose_name='Middle Name')
    last_name = models.CharField(max_length=255, blank=True, verbose_name='Last Name')
    name_suffix = models.CharField(max_length=255, blank=True, verbose_name='Suffix')
    mailing_address = models.ManyToManyField(Property, related_name='contacts_as_mailing_address', blank=True, verbose_name='Mailing Address')
    wireless = models.ManyToManyField(Wireless_Number, related_name='contact_as_wireless', blank=True, verbose_name='Wireless Numbers')
    landline = models.ManyToManyField(Landline_Number, related_name='contact_as_landline', blank=True, verbose_name='Landline Numbers')
    emails = models.ManyToManyField(Email, related_name='contact_as_email', blank=True, verbose_name='Email Addresses')
    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'

# ------------------------------------------------------------- #

class Court_Record(OperationStat):
    state = models.CharField(max_length=100, blank=True, verbose_name='State')
    county = models.CharField(max_length=100, blank=True, verbose_name='County')
    case_number = models.CharField(max_length=255, blank=True, verbose_name='Case Number')
    court_name = models.CharField(max_length=255, blank=True, verbose_name='Court Name')
    case_type = models.CharField(max_length=255, blank=True, verbose_name='Case Type')
    property = models.ManyToManyField(Property, blank=True, related_name='court_records', verbose_name='Property')
    case_status = models.CharField(max_length=255, blank=True, verbose_name='Case Status')
    plaintiff = models.ForeignKey(Contact, blank=True, related_name='court_records_as_plaintiff', default="", on_delete=models.CASCADE, verbose_name='Plaintiff')
    defendant = models.ForeignKey(Contact, blank=True, related_name='court_records_as_defendant', default="", on_delete=models.CASCADE, verbose_name='Defendant')
    class Meta:
        verbose_name = 'Court Record'
        verbose_name_plural = 'Court Records'

# ------------------------------------------------------------- #

class Transaction(OperationStat):
    DEED = 'deed'
    LIEN = 'lien'
    LOAN = 'loan'
    RELEASE = 'release'
    TR_TYPE = (
        (DEED, 'Deed'),
        (LOAN, 'Loan'),
        (LIEN, 'Lien'),
        (RELEASE, 'Release')
        )
    property = models.ManyToManyField(Property, related_name='transactions_as_property', verbose_name='Property')
    transaction_type = models.CharField(max_length=255, choices=TR_TYPE, default='Transaction Type', verbose_name='Transaction Type')
    instrument_no = models.CharField(max_length=255, blank=True, verbose_name='Instrument No')
    amount = models.DecimalField(max_digits=16, blank=True, decimal_places=2, verbose_name='Transaction Amount')
    first_party = models.ManyToManyField(Contact, related_name='transactions_as_first_party', blank=True, verbose_name='First Party - Grantor, Seller, Borrower)')
    second_party = models.ManyToManyField(Contact, related_name='transactions_as_second_party', blank=True, verbose_name='Second Party - Grantee, Buyer, Lender')
    third_party = models.ManyToManyField(Contact, related_name='transactions_as_third_party', blank=True, verbose_name='Third Party - Trustee, Guarantor, Attorney')
    comment = models.CharField(max_length=255, blank=True, verbose_name='Comment')
    reference_transaction = models.CharField(max_length=255, blank=True, verbose_name='Reference Transaction')
# ------------------------------------------------------------- #



class Foreclosure(OperationStat):
    state = models.CharField(max_length=225)
    county = models.CharField(max_length=225)
    court_record_id = models.ForeignKey(Court_Record, blank=True, related_name='court_record_id_for_foreclosure', default="", on_delete=models.CASCADE, verbose_name='Case id')
    sale_date = models.DateField(blank=True)
    sale_type = models.CharField(max_length=225)
    sale_status = models.CharField(max_length=225)
    fcl_final_judgment = models.DecimalField(decimal_places=2, max_digits=10)
    sale_price = models.DecimalField(decimal_places=2, max_digits=10)
    possible_surplus = models.DecimalField(decimal_places=2, max_digits=10)
    verified_surplus = models.DecimalField(decimal_places=2, max_digits=10)
    comment = models.CharField(max_length=225, blank=True)
    hidden_for = models.ManyToManyField(User, related_name='hidden_leads', blank=True)
    purchased_by = models.ManyToManyField(User, related_name='purchased_leads', blank=True)
    archived_by = models.ManyToManyField(User, related_name='archived_leads', blank=True)

class Status(models.Model):
    NOT_SIGNED = 'not signed'
    AGREEMENT_MAILED = 'agreement mailed'
    AGREEMENT_SIGNED = 'agreement signed'
    AG_STATUS = (
        (NOT_SIGNED, 'Not Signed'),
        (AGREEMENT_MAILED, 'Agreement Mailed'),
        (AGREEMENT_SIGNED, 'Agreement Signed')
        )
    PREPARING_DOCUMENTS = 'preparing documents'
    CLAIM_SUBMITTED = 'claim submitted'
    WAITING_FOR_COURTS_DECISION = 'waiting for courts decision'
    FUND_DISBURSED = 'fund disbursed'
    CLAIM_SATUS = (
        (NOT_SIGNED, 'Not Signed'),
        (PREPARING_DOCUMENTS, 'Preparing Documents'),
        (CLAIM_SUBMITTED, 'Claim Submitted'),
        (WAITING_FOR_COURTS_DECISION, 'Waiting for Courts Decision'),
        (FUND_DISBURSED, 'Fund Disbursed')
        )
    client = models.ManyToManyField(User, blank=True, related_name='user_as_client')
    lead = models.ManyToManyField(Foreclosure, blank=True, related_name='status_for_lead')
    call_status = models.CharField(max_length=255, blank=True, default='Need to Call')
    call_comment = models.TextField(max_length=500, blank=True)
    agreement_status = models.CharField(max_length=255, blank=True, choices=AG_STATUS, default='Not Signed')
    agreement_comment = models.TextField(max_length=500, blank=True)
    claim_status = models.CharField(max_length=255, blank=True, choices=CLAIM_SATUS, default='Not Signed')
    claim_comment = models.TextField(max_length=500, blank=True)
    

