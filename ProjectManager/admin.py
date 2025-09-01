from django.contrib import admin
from .models import *

@admin.register(Projects)
class ProjectsAdmin(admin.ModelAdmin):
    list_display = ('name','description')

@admin.register(UpdateCycle)
class UpdateCycleAdmin(admin.ModelAdmin):
    list_display = ('year','week','cycle_start','cycle_end','status')

@admin.register(TasksTemplate)
class TasksTemplateAdmin(admin.ModelAdmin):
    list_display = ('project','weekday','task_name','task_group','archived')

@admin.register(Tasks)
class TasksAdmin(admin.ModelAdmin):
    list_display = ('project','cycle','task_name','task_group','date_assigned','delivery_date','status')
    
@admin.register(TaskViews)
class TaskViewsAdmin(admin.ModelAdmin):
    list_display = ('viewname','taskname','weekday','duration','group')

@admin.register(TimeTracker)
class TimeTrackerAdmin(admin.ModelAdmin):
    list_display = ('task','user','start_time','end_time','is_paused')