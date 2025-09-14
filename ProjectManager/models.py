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