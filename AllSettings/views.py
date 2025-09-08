from django.shortcuts import render
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import json

# core/views.py


@csrf_exempt
@login_required
def save_sidebar_setting(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        expanded = data.get('expanded', True)
        setting = GeneralSettings.objects.get_or_create(user=request.user)[0]
        setting.sidebar_expanded = expanded
        setting.save()
        return JsonResponse({'status': 'saved'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt  # (better: use CSRF token properly, see above)
def update_client_filter_display_setting(request):
    if request.method == "POST":
        data = json.loads(request.body)
        field = data.get("field")
        value = data.get("value")
        
        client_settings, created = ClientSettings.objects.get_or_create(user=request.user)

        if hasattr(client_settings, field):
            setattr(client_settings, field, value)
            client_settings.save()
            return JsonResponse({"success": True, "field": field, "value": value})
        else:
            return JsonResponse({"success": False, "error": "Invalid field"}, status=400)
    
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)