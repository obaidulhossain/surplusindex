from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from Admin.utils.threadlocal import get_current_user
from builtins import property as builtin_property
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


    class Meta:
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'
        
    @property
    def street_address (self):
        street_parts = [
                self.house_number,
                self.road_name,
                self.road_type,
                self.direction,
                self.apt_unit,
                self.extention,
            ]
        full_street = " ".join(filter(None, [part.strip() for part in street_parts if part]))
        return full_street
    
    # def __str__(self):
    #     return f"{self.house_number} {self.road_name} {self.road_type} {self.direction} {self.apt_unit} {self.extention}, {self.city}, {self.state} {self.zip_code}"
    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.state} {self.zip_code}"
    
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
        if self.individual_name and self.business_name:
            return f"{self.business_name} | {self.individual_name}"
        elif self.individual_name:
            return self.individual_name
        else:
            return self.business_name
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
        # Build name parts dynamically, skipping blanks
        name_parts = [
            self.name_prefix,
            self.first_name,
            self.middle_name,
            self.last_name,
            self.name_suffix,
        ]
        full_name = " ".join(filter(None, [part.strip() for part in name_parts if part]))

        # Add designation and business_name only if they exist
        designation = self.designation.strip() if self.designation else ""
        business = self.business_name.strip() if self.business_name else ""

        # Build the final string smartly
        if designation and business:
            return f"{full_name} : {designation} : {business}"
        elif designation:
            return f"{full_name} : {designation}"
        elif business:
            if full_name:
                return f"{full_name} : {business}"
            else:
                return business
        else:
            return full_name or "Unnamed Contact"
        #return f"{self.name_prefix} {self.first_name} {self.middle_name} {self.last_name} {self.name_suffix} | {self.designation} : {self.business_name}"

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

    ACTIVE = 'active'
    SOLD = 'sold'
    UNSOLD = 'unsold'
    CANCELLED = 'cancelled'
    SOLD_TO_PLAINTIFF = 'sold to plaintiff'
    BANKRUPTCY_HOLD = 'bankruptcy hold'
    SALE_STATUS = (
        (ACTIVE, 'Active'),
        (SOLD, 'Sold'),
        (UNSOLD, 'Unsold'),
        (CANCELLED, 'Cancelled'),
        (SOLD_TO_PLAINTIFF, 'Sold To Plaintiff'),
        (BANKRUPTCY_HOLD, 'Bankruptcy Hold'),
    )

    TAX = 'tax'
    MORTGAGE = 'mortgage'
    SALE_TYPE = ((TAX, 'Tax'), (MORTGAGE, 'Mortgage'))

    state = models.CharField(max_length=225, null=True)
    county = models.CharField(max_length=225,  null=True)
    case_number = models.CharField(max_length=255, null=True, blank=True, verbose_name='Case Number')
    case_number_ext = models.CharField(max_length=10, blank=True, verbose_name='Case Extension',default="")
    court_name = models.CharField(max_length=255, blank=True, verbose_name='Court Name')
    case_type = models.CharField(max_length=255, blank=True, verbose_name='Case Type')
    property = models.ManyToManyField(Property, blank=True, related_name='court_records', verbose_name='Property')
    case_status = models.CharField(max_length=255, blank=True, verbose_name='Case Status')
    plaintiff = models.ManyToManyField(ForeclosingEntity, blank=True, related_name='plaintiff_for_foreclosure', default="", verbose_name='Plaintiff')
    defendant = models.ManyToManyField(Contact, blank=True, related_name='defendant_for_foreclosure', default="", verbose_name='Defendant')
    sale_date = models.DateField(blank=True, null=True)
    sale_type = models.CharField(max_length=225, choices=SALE_TYPE, null=True, blank=True)
    sale_status = models.CharField(max_length=225, choices=SALE_STATUS, null=True, blank=True)
    appraised_value = models.DecimalField(decimal_places=2, max_digits=15, null=True, blank=True)
    fcl_final_judgment = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    sale_price = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    possible_surplus = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    verified_surplus = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    surplus_status = models.CharField(max_length=100, choices=SURPLUS_STATUS, default="Not Determined", null=True, blank=True)
    comment = models.CharField(max_length=225, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    hidden_for = models.ManyToManyField(User, related_name='hidden_leads', blank=True)
    purchased_by = models.ManyToManyField(User, related_name='purchased_leads', blank=True)
    archived_by = models.ManyToManyField(User, related_name='archived_leads', blank=True)
    case_search_assigned_to = models.ForeignKey(User,related_name='case_assigned_to',blank=True, null=True, on_delete=models.CASCADE)
    case_search_updated = models.DateField(null=True, blank=True)
    case_search_status = models.CharField(max_length=100, choices=CASE_SEARCH_STATUS, null=True, blank=True)
    published = models.BooleanField(default=False)
    auction_source = models.CharField(max_length=255, null=True, blank=True)
    def update_possible_surplus(self):
        try:
            sale_price = float(self.sale_price)
            fcl_final_judgment = float(self.fcl_final_judgment)
            self.possible_surplus = sale_price - fcl_final_judgment
            self.save(update_fields=["possible_surplus"])
        except (ValueError, TypeError) as e:
            # Handle the error, log it, or set a default value
            self.possible_surplus = None
            print(f"Error calculating possible_surplus: {e}")
            self.save(update_fields=["possible_surplus"])

    class Meta:
        verbose_name = 'Foreclosure'
        verbose_name_plural = 'Foreclosures'

    def __str__(self):
        return f"{self.case_number} | {self.state} {self.county}"
    @builtin_property
    def fcl_case_lookup(self):
        return " : ".join( v.strip() for v in [self.state, self.county, self.case_number, self.case_number_ext,] if v )





class Status(OperationStat):
    client = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name='user_as_client', default=1)
    lead = models.ForeignKey(Foreclosure, blank=True, related_name='foreclosure_as_lead', on_delete=models.CASCADE, default=1)   
    archived = models.BooleanField(default=False)
    #----------------------------------------- Prospecting timeline section
    #-----Find The Right Contact Section------------------------Start------
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

    PENDING = 'pending'
    SKIPTRACED_FOUND = 'skiptraced_found'
    SKIPTRACED_NOT_FOUND = 'skiptraced_not_found'
    COLD_CALLING_LOCATED = 'cold_calling_located'
    COLD_CALLING_NOT_LOCATED = 'cold_calling_not_located'
    SKIPSTATUS = (
        (PENDING, 'Pending'),
        (SKIPTRACED_FOUND, 'Skiptraced Found'),
        (SKIPTRACED_NOT_FOUND, 'Skiptraced Not Found'),
        (COLD_CALLING_LOCATED, 'Cold Calling Located'),
        (COLD_CALLING_NOT_LOCATED, 'Cold Calling Not Located'),
    )

    find_contact_status = models.CharField(max_length=255, blank=True, choices=CONTACTSTATUS, default="NOT_ASSIGNED")
    skiptracing_status = models.CharField(max_length=255, blank=True, choices=SKIPSTATUS, default="PENDING")
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
    #-----Call and Negotiate Section--------------------------Start--------
    NEED_TO_CALL = 'need_to_call'
    RESPONDED = 'responded'
    NOT_RESPONDED = 'not_responded'
    RE_SKIPTRACE = 're_skiptrace'
    CN_STATUS = (
        (NEED_TO_CALL, 'Need to Call'),
        (RESPONDED, 'Responded'),
        (NOT_RESPONDED, 'Not Responded'),
        (RE_SKIPTRACE, 'Re Skiptrace'),
    )
    INTERESTED = 'interested'
    NOT_INTERESTED = 'not_interested'
    NOT_SURE = 'not_sure'
    NG_STATUS = (
        (INTERESTED, 'Interested'),
        (NOT_INTERESTED, 'Not Interested'),
        (NOT_SURE, 'Not Sure'),
    )
    call_status = models.CharField(max_length=255, blank=True, choices=CN_STATUS, default='NEED_TO_CALL')  
    negotiation_status = models.CharField(max_length=255, blank=True, choices=NG_STATUS)
    #-----------follow up section model reference: Clients>models.py>FollowUp----------
    #-----Close the deal Section------------------------------------------Start--------
    PREPARING_DOCUMENTS = 'preparing_documents'
    AGREEMENT_SENT = 'agreement_sent'
    CONVERSION_IN_PROGRESS = 'conversion_in_progress'
    CLOSED_FUNDED = 'closed_funded'
    CLOSED_NOT_FUNDED = 'closed_not_funded'
    CL_STATUS = (
        (PREPARING_DOCUMENTS, 'Preparing Documents'),
        (AGREEMENT_SENT, 'Agreement Sent'),
        (CONVERSION_IN_PROGRESS, 'Conversion In Progress'),
        (CLOSED_FUNDED, 'Closed Funded'),      
        (CLOSED_NOT_FUNDED, 'Closed Not Funded')
        )
    closing_status = models.CharField(max_length=255, blank=True, choices=CL_STATUS)
    
    NOT_STARTED = 'not_started'
    STARTED = 'started'
    PREPARED = 'prepared'
    MAILED = 'mailed'
    PREP_DOC_STATUS = (
        (NOT_STARTED, 'Not Started'),
        (STARTED, 'Started'),
        (PREPARED, 'Prepared'),
        (MAILED, 'Mailed'),
    )
    doc_status = models.CharField(max_length=255, blank=True, choices=PREP_DOC_STATUS)

    NOT_DELIVERED = 'not_delivered'
    DELIVERED = 'delivered'
    RETURNED_SIGNED = 'returned_signed'
    RETURNED_NOT_SIGNED = 'returned_not_signed'
    AG_SENT_STATUS = (
        (NOT_DELIVERED, 'Not Delivered'),
        (DELIVERED, 'Delivered'),
        (RETURNED_SIGNED, 'Returned Signed'),
        (RETURNED_NOT_SIGNED, 'Returned Not Signed'),
    )
    ag_sent_status = models.CharField(max_length=255, blank=True, choices=AG_SENT_STATUS)
    
    ATT_SUBMIT = 'attorney_submit'
    DIRECT_SUBMIT = 'direct_submit'
    MOTION_GRANTED = 'motion_granted'
    MOTION_DENIED = 'motion_denied'
    LPROCEDURES_STATUS = (
        (ATT_SUBMIT, 'Attorney Submit'),
        (DIRECT_SUBMIT, 'Direct Submit'),
        (MOTION_GRANTED, 'Motion Granted'),
        (MOTION_DENIED, 'Motion Denied')
    )
    lp_status = models.CharField(max_length=255, blank=True, choices=LPROCEDURES_STATUS)

    total_disbursed = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fee_agreement_share = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    attorney_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_costs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    def update_net_profit(self):
        self.net_profit = self.total_disbursed - self.fee_agreement_share - self.attorney_cost - self.other_costs
        self.save()
    