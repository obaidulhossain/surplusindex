from .models import *

def sidebar_setting(request):
    if request.user.is_authenticated:
        try:
            setting = GeneralSettings.objects.get(user=request.user)
            return {'sidebar_expanded': setting.sidebar_expanded}
        except GeneralSettings.DoesNotExist:
            return {'sidebar_expanded': True}
    return {'sidebar_expanded': True}