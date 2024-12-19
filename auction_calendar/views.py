from django.http import HttpResponse
from django.template import loader

# Create your views here.

def auction_calendar (request):
    template = loader.get_template('auction_calendar.html')
    return HttpResponse(template.render())

def dashboard (request):
    template = loader.get_template('dashboard.html')
    return HttpResponse(template.render())

