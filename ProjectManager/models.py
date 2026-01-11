from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from propertydata.models import*
from si_user.models import*
# Create your models here.
class Timelogger(models.Model):
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created')
    changed_at = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name='Updated')
    class Meta:
        abstract = True

class Projects(Timelogger):
    name = models.CharField(max_length=255)
    state = models.CharField(max_length=255, null=True, blank=True)
    sale_type = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255)
    post_foreclosure_update_interval = models.IntegerField(default=7)
    active = models.BooleanField(default=True)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return self.name

class TaskViews(Timelogger):
    viewname = models.CharField(max_length=255, blank=True)
    taskname = models.CharField(max_length=255, blank=True)
    weekday = models.CharField(max_length=255, choices=[
        ("1","Monday"),
        ("2","Tuesday"),
        ("3","Wednesday"),
        ("4","Thursday"),
        ("5","Friday"),
        ("6","Saturday"),
        ("7","Sunday"),
    ])
    duration = models.IntegerField(blank=True)
    group = models.CharField(max_length=255, null=True, blank=True, choices=[
        ("datask","Data Entry"),
        ("admintask","Admin Task")
    ])
    def __str__(self):
        return self.viewname

class UpdateCycle(Timelogger):
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    year = models.CharField(max_length=100)
    week = models.IntegerField()
    cycle_start = models.DateField()
    cycle_end = models.DateField()
    sale_from = models.DateField()
    sale_to = models.DateField()
    completed = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=255, choices=[
        ("backlog", "Backlog"),
        ("active", "Active"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("closed", "Closed"),
    ])
    pf_list = models.URLField(null=True, blank=True)
    def __str__(self):
        return f"{self.year} : Week - {self.week}"

class TasksTemplate(Timelogger):
    taskview = models.ForeignKey(TaskViews, on_delete=models.CASCADE, null=True)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    weekday = models.CharField(max_length=255, choices=[
        ("1","Monday"),
        ("2","Tuesday"),
        ("3","Wednesday"),
        ("4","Thursday"),
        ("5","Friday"),
        ("6","Saturday"),
        ("7","Sunday"),
    ])
    task_duration = models.IntegerField(blank=True)
    task_group = models.CharField(max_length=255, null=True, blank=True, choices=[
        ("datask","Data Entry"),
        ("admintask","Admin Task")
    ])
    task_name = models.CharField(max_length=255, null=True, blank=True)
    job_detail = models.TextField(null=True, blank=True)
    assigned_to = models.ManyToManyField(User, blank=True)
    archived = models.BooleanField(default=False)
    def __str__(self):
        return self.task_name

class Tasks(Timelogger):
    cycle = models.ForeignKey(UpdateCycle, on_delete=models.CASCADE, related_name="tasks")
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name="tasks")
    template = models.ForeignKey(TasksTemplate, on_delete=models.CASCADE, related_name="tasks", null=True )
    task_name = models.CharField(max_length=255, blank=True, null=True)
    task_group = models.CharField(max_length=255, choices=[
        ("datask","Data Entry"),
        ("admintask","Admin Task")
    ])
    date_assigned = models.DateField(blank=True, null=True)
    assigned_to = models.ManyToManyField(User, related_name="assigned_tasks", blank=True)
    delivery_date = models.DateField(blank=True, null=True)
    reporting_date = models.DateField(blank=True, null=True)
    description = models.TextField(null=True,blank=True)
    note = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, choices=[
        ("created","Created"),
        ("assigned","Assigned"),
        ("delivered","Delivered"),
        ("completed","Completed"),
    ], default="created")
    time_captured = models.IntegerField(default=0, help_text="Total time spent in seconds")
    tracker_status = models.CharField(max_length=255, choices=[
        ("idle","Idle"),
        ("started","Started"),
        ("paused","Paused"),
        ("stopped","Stopped"),
    ], default="idle")
    lead_volume = models.CharField(max_length=255, blank=True, null=True)
    contact_volume = models.CharField(max_length=255, blank=True, null=True)
    case_searched = models.CharField(max_length=255, blank=True, null=True)
    skiptraced = models.CharField(max_length=255, blank=True, null=True)
    published = models.CharField(max_length=255, blank=True, null=True)
    post_foreclosure_case_volume = models.CharField(max_length=255, blank=True, null=True)
    post_foreclosure_cases = models.ManyToManyField(Foreclosure, blank=True)
    post_foreclosure_case_searched = models.CharField(max_length=255, blank=True, null=True)
    active_subscribers = models.ManyToManyField(StripeSubscription, blank=True)


    def __str__(self):
        return self.task_name or f"Task {self.id}"
    
    def get_time_display(self):
        """Return captured time in HH:MM:SS format"""
        import datetime
        return str(datetime.timedelta(seconds=self.time_captured))
    def get_current_status(self, user):
        tracker = self.time_logs.filter(user=user, end_time__isnull=True).last()
        if tracker:
            return "running"
        # last tracker closed but not resumed → paused
        tracker = self.time_logs.filter(user=user).last()
        if tracker and tracker.end_time and not tracker.is_paused:
            return "paused"
        return "stopped"

class DeliveryReport(Timelogger):
    task = models.ForeignKey(Tasks, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    delivered = models.IntegerField(default=0)
    report = models.CharField(max_length=255, blank=True, null=True)




class TimeTracker(models.Model):
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE, related_name="time_logs")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="time_logs")
    start_time = models.DateTimeField(default=now)
    end_time = models.DateTimeField(null=True, blank=True)
    is_paused = models.BooleanField(default=False)

    def duration(self):
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0
    
class ProjectIssues(Timelogger):
    type = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=255, choices=[
        ("open","Open"),
        ("resolved","Resolved"),
        ("unsolved","Unsolved"),
        ("closed","Closed"),
    ], default="open")
    def __str__(self):
        return f"{self.user.username} created a {self.type} issue: {self.title} : {self.description}"

class TemporaryData(Timelogger):
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
    ACTIVE = 'pending'
    SOLD = 'sold'
    UNSOLD = 'unsold'
    CANCELLED = 'cancelled'
    SOLD_TO_PLAINTIFF = 'sold_to_plaintiff'
    BANKRUPTCY_HOLD = 'bankruptcy_hold'
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

    #foreclosure fields
    state = models.CharField(max_length=225, null=True)
    county = models.CharField(max_length=225,  null=True)
    case_number = models.CharField(max_length=255, null=True, blank=True, verbose_name='Case Number')
    case_number_ext = models.CharField(max_length=10, blank=True, verbose_name='Case Extension',default="")
    sale_date = models.DateField(blank=True, null=True)
    sale_type = models.CharField(max_length=225, choices=SALE_TYPE, null=True, blank=True)
    appraised_value = models.DecimalField(decimal_places=2, max_digits=15, null=True, blank=True)
    fcl_final_judgment = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    sale_price = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    possible_surplus = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    verified_surplus = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    sale_status = models.CharField(max_length=225, choices=SALE_STATUS, null=True, blank=True)
    surplus_status = models.CharField(max_length=100, choices=SURPLUS_STATUS, default="Not Determined", null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    auction_source = models.CharField(max_length=255, null=True, blank=True)
    case_lookup = models.CharField(max_length=255, blank=True)
    #property fields
    parcel = models.CharField(max_length=255, blank=True, verbose_name='Parcel ID')
    house_number = models.CharField(max_length=255, blank=True, verbose_name='House')
    road_name = models.CharField(max_length=255, blank=True, verbose_name='Road')
    road_type = models.CharField(max_length=255, blank=True, verbose_name='Road Type')
    direction = models.CharField(max_length=255, blank=True, verbose_name='Direction')
    apt_unit = models.CharField(max_length=255, blank=True, verbose_name='Apartment/Unit')
    extention = models.CharField(max_length=255, blank=True, verbose_name='Extension')
    city = models.CharField(max_length=255, blank=True, verbose_name='City')
    zip_code = models.CharField(max_length=255, blank=True, verbose_name='Zip')
    
    #plaintiff fields
    plaintiff = models.CharField(max_length=255, blank=True)
    #defendant fields
    business_name = models.CharField(max_length=255, blank=True, verbose_name='Business Name')
    designation = models.CharField(max_length=100, blank=True, verbose_name='Designation')
    name_prefix = models.CharField(max_length=10, blank=True, verbose_name='Prefix')
    first_name = models.CharField(max_length=255, blank=True, verbose_name='First Name')
    middle_name = models.CharField(max_length=255, blank=True, verbose_name='Middle Name')
    last_name = models.CharField(max_length=255, blank=True, verbose_name='Last Name')
    name_suffix = models.CharField(max_length=10, blank=True, verbose_name='Suffix')
    s_foreclosure = models.ManyToManyField(Foreclosure, blank=True, related_name="suggested_fcl")
    s_property = models.ManyToManyField(Property, blank=True, related_name="suggested_prop")
    s_defendant = models.ManyToManyField(Contact, blank=True, related_name="suggested_def")
    s_plaintiff = models.ManyToManyField(ForeclosingEntity, blank=True, related_name="suggested_plt")
    u_foreclosure = models.ManyToManyField(Foreclosure, blank=True, related_name="update_fcl")
    u_property = models.ManyToManyField(Property, blank=True, related_name="update_prop")
    u_defendant = models.ManyToManyField(Contact, blank=True, related_name="update_def")
    u_plaintiff = models.ManyToManyField(ForeclosingEntity, blank=True, related_name="update_plt")
    
    CREATED = 'created'
    UPDATED = 'updated'
    DATA_STATUS = ((CREATED, 'Created'), (UPDATED, 'Updated'))
    update_status = models.CharField(max_length=255,choices=DATA_STATUS, blank=True, default="created")
    
    NEW = 'new'
    EXIST = 'exist'
    AVAILABILITY = ((NEW, 'New'), (EXIST, 'Exist'))
    update_type = models.CharField(max_length=255,choices=AVAILABILITY, blank=True, default="new")
    @property
    def full_address (self):
        street_parts = [
                self.house_number,
                self.road_name,
                self.road_type,
                self.direction,
                self.apt_unit,
                self.extention,
            ]
        full_street = " ".join(filter(None, [part.strip() for part in street_parts if part]))
        return f"{full_street}, {self.city}, {self.state} {self.zip_code}"
        

class Upload(Timelogger):
    name = models.CharField(max_length=255)
    data = models.ManyToManyField(TemporaryData)
    
    PENDING = 'pending'
    COMPLETED = 'completed'
    STATUS = ((PENDING, 'Pending'), (COMPLETED, 'Completed'))
    status = models.CharField(max_length=255,choices=STATUS, default="pending")