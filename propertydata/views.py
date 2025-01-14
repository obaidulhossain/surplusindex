from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'propertydata/index.html')

def addproperty(request):
    return render(request, 'propertydata/addproperty.html')