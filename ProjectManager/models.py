from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Timelogger(models.Model):
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created')
    changed_at = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name='Updated')
    class Meta:
        abstract = True

class Projects(Timelogger):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    def __str__(self):
        return self.name

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
    def __str__(self):
        return f"{self.year} : Week - {self.week}"

class TasksTemplate(Timelogger):
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

class Tasks(Timelogger):
    cycle = models.ForeignKey(UpdateCycle, on_delete=models.CASCADE, related_name="tasks")
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name="tasks")
    template = models.ForeignKey(TasksTemplate, on_delete=models.CASCADE, related_name="tasks", null=True )
    task_name = models.CharField(max_length=255, blank=True, null=True)
    task_group = models.CharField(max_length=255, choices=[
        ("datask","Data Entry"),
        ("admintask","Admin Task")
    ])
    date_assigned = models.DateField()
    assigned_to = models.ManyToManyField(User, related_name="assigned_tasks", blank=True)
    delivery_date = models.DateField()
    reporting_date = models.DateField()
    description = models.TextField(null=True,blank=True)
    note = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, choices=[
        ("created","Created"),
        ("assigned","Assigned"),
        ("delivered","Delivered"),
        ("completed","Completed"),
    ], default="created")