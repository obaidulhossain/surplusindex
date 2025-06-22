from django.contrib import admin
from .models import *



class FollowupAdmin(admin.ModelAdmin):
    list_display = ('leads_id','followup_date', 'f_note','f_result', 'f_status')
# Register your models here.

class ActionHistoryAdmin(admin.ModelAdmin):
    list_display = ('lead_id','created_at', 'action_source','action_type', 'action', 'details')

admin.site.register(FollowUp, FollowupAdmin)
admin.site.register(ActionHistory, ActionHistoryAdmin)

