from django.shortcuts import render
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required(login_url="login")
def index(request):
    return render(request, 'propertydata/index.html')

@login_required(login_url="login")
def addproperty(request):
    return render(request, 'propertydata/addproperty.html')