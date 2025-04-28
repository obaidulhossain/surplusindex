from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from Admin.utils.threadlocal import get_current_user
# ----- CHOICES FOR GLOBAL USE -------------------------------- # 
ACTIVE = 'active'                                               # 
INACTIVE = 'inactive'                                           # 
STATUSCHOICES = (                                               # 
    (ACTIVE, 'Active'),                                         # 
    (INACTIVE, 'Inactive')                                      # 
    )                                                           # 
# ----- CHOICES FOR GLOBAL USE -------------------------------- # 

# ------------------------------------------------------------- #
import logging
logger = logging.getLogger(__name__)
# ----- ABSTRACT CLASS TO BE USED IN OTHER MODELS ------------- # 
class OperationStat(models.Model):                              #
    created_at = models.DateTimeField(auto_now_add=True)        #
    changed_at = models.DateTimeField(null=True, blank=True)            #
    class Meta:                                                 #
        abstract = True                                         #
    def save(self, *args, **kwargs):
        user = get_current_user()  # Get the user from thread-local storage
        if user and user.groups.filter(name="researcher").exists():
            self.changed_at = now()
        else:
            if self.pk:
                existing = self.__class__.objects.get(pk=self.pk)
                self.changed_at = existing.changed_at
        super().save(*args, **kwargs)


        # if user:
        #     # Check if the user belongs to 'client' or 'admin' groups
            
        #     user_groups = {group.name for group in user.groups.all()}
        #     print(user_groups)
        #     restricted_groups = {"client", "admin"}
        #     if restricted_groups.intersection(user_groups):

        #         if self.pk:  # If instance exists, fetch the current `changed_at` value
        #             existing = self.__class__.objects.get(pk=self.pk)
        #             self.changed_at = existing.changed_at  # Preserve the original `changed_at` value



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

    def __str__(self):
        return f"{self.house_number} {self.road_name} {self.road_type} {self.direction} {self.apt_unit} {self.extention}, {self.city}, {self.state} {self.zip_code}"
    
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
    
    def __str__(self):
        return self.email_address
# ------------------------------------------------------------- #

class Wireless_Number(models.Model):
    w_number = models.CharField(max_length=255, blank=True, verbose_name='Wireless Number')
    w_caller_id = models.CharField(max_length=255, blank=True, verbose_name='Wireless Caller ID')
    w_status = models.CharField(max_length=255, choices=STATUSCHOICES, default=ACTIVE, verbose_name='Status')

    class Meta:
        verbose_name = 'Wireless Number'
        verbose_name_plural = 'Wireless Numbers'
    
    def __str__(self):
        return self.w_number

# ------------------------------------------------------------- #

class Landline_Number(models.Model):
    l_number = models.CharField(max_length=255, blank=True, verbose_name='Landline Number')
    l_caller_id = models.CharField(max_length=255, blank=True, verbose_name='Landline Caller ID')
    l_status = models.CharField(max_length=255, choices=STATUSCHOICES, default=ACTIVE, verbose_name='Status')

    class Meta:
        verbose_name = 'Landline Number'
        verbose_name_plural = 'Landline Numbers'
    def __str__(self):
        return self.l_number

# ------------------------------------------------------------- #

class ForeclosingEntity(models.Model):
    individual_name = models.CharField(max_length=255, blank=True)
    business_name = models.CharField(max_length=255, blank=True)
    dba = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.business_name} | {self.individual_name}"


# ------------------------------------------------------------- #

class Contact(OperationStat):
    business_name = models.CharField(max_length=255, blank=True, verbose_name='Business Name')
    designation = models.CharField(max_length=100, blank=True, verbose_name='Designation')
    name_prefix = models.CharField(max_length=10, blank=True, verbose_name='Prefix')
    first_name = models.CharField(max_length=255, blank=True, verbose_name='First Name')
    middle_name = models.CharField(max_length=255, blank=True, verbose_name='Middle Name')
    last_name = models.CharField(max_length=255, blank=True, verbose_name='Last Name')
    name_suffix = models.CharField(max_length=10, blank=True, verbose_name='Suffix')
    mailing_address = models.ManyToManyField(Property, related_name='contacts_as_mailing_address', blank=True, verbose_name='Mailing Address')
    wireless = models.ManyToManyField(Wireless_Number, related_name='contact_as_wireless', blank=True, verbose_name='Wireless Numbers')
    landline = models.ManyToManyField(Landline_Number, related_name='contact_as_landline', blank=True, verbose_name='Landline Numbers')
    emails = models.ManyToManyField(Email, related_name='contact_as_email', blank=True, verbose_name='Email Addresses')
    related_contacts = models.ManyToManyField('self', blank=True, symmetrical=True)
    skp_assignedto = models.ForeignKey(User, related_name='assign_skp', on_delete=models.CASCADE, blank=True, null=True)
    skiptraced = models.BooleanField(default=False)
    skiptrace_comment = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.name_prefix} {self.first_name} {self.middle_name} {self.last_name} {self.name_suffix} | {self.designation} : {self.business_name}"

    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'

# ------------------------------------------------------------- #

# class Court_Record(OperationStat):
#     state = models.CharField(max_length=100, blank=True, verbose_name='State')
#     county = models.CharField(max_length=100, blank=True, verbose_name='County')

#     class Meta:
#         verbose_name = 'Court Record'
#         verbose_name_plural = 'Court Records'

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
    transaction_date = models.DateField(blank=True, null=True)
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
    NOT_DETERMINED = 'not determined'
    POSSIBLE_SURPLUS = 'possible surplus'
    NO_POSSIBLE_SURPLUS = 'no possible surplus'
    FUND_AVAILABLE = 'fund available'
    MOTION_FILED = 'motion filed'
    FUND_CLAIMED = 'fund claimed'
    NO_SURPLUS = 'no surplus'
    SURPLUS_STATUS = (
        (NOT_DETERMINED, 'Not Determined'),
        (POSSIBLE_SURPLUS, 'Possible Surplus'),
        (NO_POSSIBLE_SURPLUS, 'No Possible Surplus'),
        (FUND_AVAILABLE, 'Fund Available'),
        (MOTION_FILED, 'Motion Filed'),
        (FUND_CLAIMED, 'Fund Claimed'),
        (NO_SURPLUS, 'No Surplus'),
        )
    
    PENDING = 'pending'
    COMPLETED = 'completed'
    VERIFIED = 'verified'
    CASE_SEARCH_STATUS = (
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (VERIFIED, 'Verified'),
    )

    ACTIVE = 'pending'
    SOLD = 'completed'
    CANCELLED = 'cancelled'
    SALE_STATUS = (
        (ACTIVE, 'Active'),
        (SOLD, 'Sold'),
        (CANCELLED, 'Cancelled'),
    )

    TAX = 'tax'
    MORTGAGE = 'mortgage'
    SALE_TYPE = ((TAX, 'Tax'), (MORTGAGE, 'Mortgage'))

    state = models.CharField(max_length=225)
    county = models.CharField(max_length=225)
    case_number = models.CharField(max_length=255, blank=True, verbose_name='Case Number')
    case_number_ext = models.CharField(max_length=10, blank=True, null=True, verbose_name='Case Extension')
    court_name = models.CharField(max_length=255, blank=True, verbose_name='Court Name')
    case_type = models.CharField(max_length=255, blank=True, verbose_name='Case Type')
    property = models.ManyToManyField(Property, blank=True, related_name='court_records', verbose_name='Property')
    case_status = models.CharField(max_length=255, blank=True, verbose_name='Case Status')
    plaintiff = models.ManyToManyField(ForeclosingEntity, blank=True, related_name='plaintiff_for_foreclosure', default="", verbose_name='Plaintiff')
    defendant = models.ManyToManyField(Contact, blank=True, related_name='defendant_for_foreclosure', default="", verbose_name='Defendant')
    sale_date = models.DateField(blank=True, null=True)
    sale_type = models.CharField(max_length=225, choices=SALE_TYPE, null=True, blank=True)
    sale_status = models.CharField(max_length=225, choices=SALE_STATUS, null=True, blank=True)
    fcl_final_judgment = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    sale_price = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    possible_surplus = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    verified_surplus = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    surplus_status = models.CharField(max_length=100, choices=SURPLUS_STATUS, default="Not Determined", null=True, blank=True)
    comment = models.CharField(max_length=225, blank=True)
    hidden_for = models.ManyToManyField(User, related_name='hidden_leads', blank=True)
    purchased_by = models.ManyToManyField(User, related_name='purchased_leads', blank=True)
    archived_by = models.ManyToManyField(User, related_name='archived_leads', blank=True)
    case_search_assigned_to = models.ForeignKey(User,related_name='case_assigned_to',blank=True, null=True, on_delete=models.CASCADE)
    case_search_updated = models.DateField(null=True, blank=True)
    case_search_status = models.CharField(max_length=100, choices=CASE_SEARCH_STATUS, blank=True)
    published = models.BooleanField(default=False)
    def update_possible_surplus(self):
        try:
            sale_price = float(self.sale_price)
            fcl_final_judgment = float(self.fcl_final_judgment)
            self.possible_surplus = sale_price - fcl_final_judgment
        except (ValueError, TypeError) as e:
            # Handle the error, log it, or set a default value
            self.possible_surplus = None
            print(f"Error calculating possible_surplus: {e}")
            self.save()

    class Meta:
        verbose_name = 'Foreclosure'
        verbose_name_plural = 'Foreclosures'

    def __str__(self):
        return f"{self.case_number} | {self.state} {self.county}"





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
    CLAIM_STATUS = (
        (NOT_SIGNED, 'Not Signed'),
        (PREPARING_DOCUMENTS, 'Preparing Documents'),
        (CLAIM_SUBMITTED, 'Claim Submitted'),
        (WAITING_FOR_COURTS_DECISION, 'Waiting for Courts Decision'),
        (FUND_DISBURSED, 'Fund Disbursed')
        )
    NOT_ASSIGNED = 'not_assigned'
    ASSIGNED = 'assigned'
    COMPLETED = 'completed'
    VERIFIED = 'verified'
    CONTACTSTATUS = (
        (NOT_ASSIGNED,'Not Assigned'),
        (ASSIGNED, 'Assigned'),
        (COMPLETED, 'Completed'),
        (VERIFIED, 'Verified'),
    )
    
    client = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name='user_as_client', default=1)
    lead = models.ForeignKey(Foreclosure, blank=True, related_name='foreclosure_as_lead', on_delete=models.CASCADE, default=1)
    
    call_status = models.CharField(max_length=255, blank=True, default='Need to Call')
    call_comment = models.TextField(max_length=500, blank=True)
    agreement_status = models.CharField(max_length=255, blank=True, choices=AG_STATUS, default='Not Signed')
    agreement_comment = models.TextField(max_length=500, blank=True)
    claim_status = models.CharField(max_length=255, blank=True, choices=CLAIM_STATUS, default='Not Signed')
    claim_comment = models.TextField(max_length=500, blank=True)
    archived = models.BooleanField(default=False)
    find_contact_status = models.CharField(max_length=255, blank=True, choices=CONTACTSTATUS, default="Not Assigned")
    first_contact_name = models.CharField(max_length=100, blank=True, null=True)
    first_contact_email = models.CharField(max_length=100, blank=True, null=True)
    first_contact_phone = models.CharField(max_length=14, blank=True, null=True)
    first_contact_address = models.CharField(max_length=100, blank=True, null=True)
    first_contact_comment = models.CharField(max_length=255, blank=True, null=True)
    second_contact_name = models.CharField(max_length=100, blank=True, null=True)
    second_contact_email = models.CharField(max_length=100, blank=True, null=True)
    second_contact_phone = models.CharField(max_length=14, blank=True, null=True)
    second_contact_address = models.CharField(max_length=100, blank=True, null=True)
    second_contact_comment = models.CharField(max_length=255, blank=True, null=True)
    find_contact_notes = models.CharField(max_length=255, blank=True)
    
    
    call_negotiate_status = models.CharField(max_length=255, choices=CONTACTSTATUS, blank=True)
    call_negotiate_comment = models.TextField(max_length=500, blank=True)
    follow_up_status = models.CharField(max_length=255, blank=True)
    follow_up_comment = models.TextField(max_length=500, blank=True)
    paperwork_status = models.CharField(max_length=255, blank=True)
    paperwork_comment = models.TextField(max_length=500, blank=True)
    fund_confirm_status = models.CharField(max_length=255, blank=True)
    fund_confirm_comment = models.TextField(max_length=500, blank=True)
    submit_paperwork_status = models.CharField(max_length=255, blank=True)
    submit_paperwork_comment = models.TextField(max_length=500, blank=True)
    waiting_status = models.CharField(max_length=255, blank=True)
    waiting_comment = models.TextField(max_length=500, blank=True)
    fund_collection_status = models.CharField(max_length=255, blank=True)
    fund_collection_comment = models.TextField(max_length=500, blank=True)
    



