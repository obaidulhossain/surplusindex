from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import ExportLeadFilter, CustomExportOptions
from .forms import ExportLeadFilterForm, CustomExportOptionsForm

# === ExportLeadFilter ===
def filter_list(request):
    filters = ExportLeadFilter.objects.all()
    return render(request, "custom_delivery/filter_list.html", {"filters": filters})

def filter_create(request):
    form = ExportLeadFilterForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Filter created successfully!")
        return redirect("filter_list")
    return render(request, "custom_delivery/filter_form.html", {"form": form, "title": "Create Filter"})

def filter_update(request, pk):
    filter_obj = get_object_or_404(ExportLeadFilter, pk=pk)
    form = ExportLeadFilterForm(request.POST or None, instance=filter_obj)
    if form.is_valid():
        form.save()
        messages.success(request, "Filter updated successfully!")
        return redirect("filter_list")
    return render(request, "custom_delivery/filter_form.html", {"form": form, "title": "Edit Filter"})

def filter_delete(request, pk):
    filter_obj = get_object_or_404(ExportLeadFilter, pk=pk)
    if request.method == "POST":
        filter_obj.delete()
        messages.success(request, "Filter deleted.")
        return redirect("filter_list")
    return render(request, "custom_delivery/confirm_delete.html", {"object": filter_obj, "type": "Filter"})


# === CustomExportOptions ===
def export_option_list(request):
    options = CustomExportOptions.objects.all()
    return render(request, "custom_delivery/option_list.html", {"options": options})

def export_option_create(request):
    form = CustomExportOptionsForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Export option created successfully!")
        return redirect("export_option_list")
    return render(request, "custom_delivery/option_form.html", {"form": form, "title": "Create Export Option"})

def export_option_update(request, pk):
    option = get_object_or_404(CustomExportOptions, pk=pk)
    form = CustomExportOptionsForm(request.POST or None, instance=option)
    if form.is_valid():
        form.save()
        messages.success(request, "Export option updated successfully!")
        return redirect("export_option_list")
    return render(request, "custom_delivery/option_form.html", {"form": form, "title": "Edit Export Option"})

def export_option_delete(request, pk):
    option = get_object_or_404(CustomExportOptions, pk=pk)
    if request.method == "POST":
        option.delete()
        messages.success(request, "Export option deleted.")
        return redirect("export_option_list")
    return render(request, "custom_delivery/confirm_delete.html", {"object": option, "type": "Export Option"})
