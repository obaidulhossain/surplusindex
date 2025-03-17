from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from .models import *
from propertydata.models import *
from .forms import *
from .resources import *
# Create your views here.




def availableLeads(request):


    context = {


    }
    return render(request, 'Client/available_leads.html', context)


# @login_required(login_url="login")
# def clientSettings(request):
#     current_user = request.user
#     if ClientSettings.objects.filter(user=current_user).exists():
#         client_settings = get_object_or_404(ClientSettings, user=current_user)
#         client_detail_form = UpdateClientDetailForm(instance=current_user)
#         detail_form = UserDetailForm(instance=current_user_detail)
#         context = {
#             'client_settings':client_settings,
#             'detail_form':detail_form,
#         }
#         return render(request, 'si_user/user_settings.html', context)
#     else:
#         UserDetail.objects.create(user=current_user)
#         return redirect('settings')



def export_data(request):
    data = Foreclosure.objects.filter(surplus_status="Fund Available").prefetch_related('defendant__wireless', 'defendant__landline', 'defendant__emails')
    resources = ClientModelResource()
    dataset = resources.export(data)
    response = HttpResponse(dataset.csv, content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="filtered_data.csv"'
    return response