from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from .models import *
from .forms import ExportLeadFilterForm, CustomExportOptionsForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from authentication.decorators import allowed_users

# === ExportLeadFilter ===
@login_required(login_url="login")
@allowed_users(['admin'])
def filter_list(request):
    filters = ExportLeadFilter.objects.all()
    return render(request, "custom_delivery/filter_list.html", {"filters": filters})


@login_required(login_url="login")
@allowed_users(['admin'])
def filter_create(request):
    form = ExportLeadFilterForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Filter created successfully!")
        return redirect("filter_list")
    return render(request, "custom_delivery/filter_form.html", {"form": form, "title": "Create Filter"})


@login_required(login_url="login")
@allowed_users(['admin'])
def filter_update(request, pk):
    filter_obj = get_object_or_404(ExportLeadFilter, pk=pk)
    form = ExportLeadFilterForm(request.POST or None, instance=filter_obj)
    if form.is_valid():
        form.save()
        messages.success(request, "Filter updated successfully!")
        return redirect("filter_list")
    return render(request, "custom_delivery/filter_form.html", {"form": form, "title": "Edit Filter"})


@login_required(login_url="login")
@allowed_users(['admin'])
def filter_delete(request, pk):
    filter_obj = get_object_or_404(ExportLeadFilter, pk=pk)
    if request.method == "POST":
        filter_obj.delete()
        messages.success(request, "Filter deleted.")
        return redirect("filter_list")
    return render(request, "custom_delivery/confirm_delete.html", {"object": filter_obj, "type": "Filter"})


# === CustomExportOptions ===
@login_required(login_url="login")
@allowed_users(['admin'])
def export_option_list(request):
    options = CustomExportOptions.objects.all()
    return render(request, "custom_delivery/option_list.html", {"options": options})


@login_required(login_url="login")
@allowed_users(['admin'])
def export_option_create(request):
    form = CustomExportOptionsForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Export option created successfully!")
        return redirect("export_option_list")
    return render(request, "custom_delivery/option_form.html", {"form": form, "title": "Create Export Option"})


@login_required(login_url="login")
@allowed_users(['admin'])
def export_option_update(request, pk):
    option = get_object_or_404(CustomExportOptions, pk=pk)
    form = CustomExportOptionsForm(request.POST or None, instance=option)
    if form.is_valid():
        form.save()
        messages.success(request, "Export option updated successfully!")
        return redirect("export_option_list")
    return render(request, "custom_delivery/option_form.html", {"form": form, "title": "Edit Export Option"})


@login_required(login_url="login")
@allowed_users(['admin'])
def export_option_delete(request, pk):
    option = get_object_or_404(CustomExportOptions, pk=pk)
    if request.method == "POST":
        option.delete()
        messages.success(request, "Export option deleted.")
        return redirect("export_option_list")
    return render(request, "custom_delivery/confirm_delete.html", {"object": option, "type": "Export Option"})


@login_required(login_url="login")
@allowed_users(['admin'])
def DeliverySettings(request):
    all_clients = CustomDeliveryClients.objects.all().order_by("name")
    context = {
        "all_clients":all_clients,
    }
    return render(request, "custom_delivery/custom_delivery_settings.html", context)


@login_required(login_url="login")
@allowed_users(['admin'])
def CreateCC(request):
    if request.method=="POST":
        client_name = request.POST.get('client-name','')
        client_email = request.POST.get('client-email','')
        contact_align = request.POST.get('contact-align','')
        columns = request.POST.get('columns','')
    else:
        client_name = request.GET.get('client-name','')
        client_email = request.GET.get('client-email','')
        contact_align = request.GET.get('contact-align','')
        columns = request.GET.get('columns','')
    CustomDeliveryClients.objects.create(
        name = client_name,
        email = client_email,
        contact_align = contact_align,
        columns = columns,
    )
    messages.success(request, "Client Instance Created for Custom Delivery")
    return redirect("delivery_settings")
    

@login_required(login_url="login")
@allowed_users(['admin'])
def CDClients(request):
    if request.method == "POST":
        clid = request.POST.get("client-id","")
    else:
        clid = request.GET.get("client-id","")
    if clid:
        client_instance = CustomDeliveryClients.objects.get(pk=clid)
    else:
        client_instance = None
    all_clients = CustomDeliveryClients.objects.all().order_by("name")
    context = {
        "client_instance":client_instance,
        "all_clients":all_clients,
    }
    return render(request, "custom_delivery/custom_delivery_clients.html", context)


@login_required(login_url="login")
@allowed_users(['admin'])
def UpdateCC(request):
    if request.method=="POST":
        client = request.POST.get('client-id','')
        client_name = request.POST.get('client-name','')
        client_email = request.POST.get('client-email','')
        contact_align = request.POST.get('contact-align','')
        columns = request.POST.get('columns','')
    else:
        client = request.GET.get('client-id','')
        client_name = request.GET.get('client-name','')
        client_email = request.GET.get('client-email','')
        contact_align = request.GET.get('contact-align','')
        columns = request.GET.get('columns','')
    if client:
        client_instance = CustomDeliveryClients.objects.get(pk=client)
        
        if client_name:
            client_instance.name = client_name
        if client_email:
            client_instance.email = client_email
        if contact_align:
            client_instance.contact_align = contact_align
        if columns:
            client_instance.columns = columns
        client_instance.save()
        messages.success(request, "Client Instance Updated")
    else:
        messages.info(request, "No Client Instance Selected")
    return redirect(f"{reverse('custom_delivery_clients')}?client-id={client_instance.id}")


@login_required(login_url="login")
@allowed_users(['admin'])
@require_POST
def remove_client_m2m(request):
    """Remove M2M relation from CustomDeliveryClients model dynamically."""
    field = request.POST.get("field")
    client_id = request.POST.get("client_id")
    related_id = request.POST.get("related_id")

    valid_fields = ["old_leads", "verified_surplus", "post_foreclosure", "pre_foreclosure"]
    if field not in valid_fields:
        return JsonResponse({"success": False, "error": "Invalid field"}, status=400)

    try:
        client = CustomDeliveryClients.objects.get(pk=client_id)
        getattr(client, field).remove(related_id)
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
