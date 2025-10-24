from django import forms
from .models import ExportLeadFilter, CustomExportOptions

class ExportLeadFilterForm(forms.ModelForm):
    class Meta:
        model = ExportLeadFilter
        fields = ["filter_name", "state", "sale_type", "sale_status", "surplus_status"]
        widgets = {
            field: forms.TextInput(attrs={"class": "form-control"}) for field in fields
        }

class CustomExportOptionsForm(forms.ModelForm):
    class Meta:
        model = CustomExportOptions
        fields = [
            "client_name", "client_email", "number_delivery", "next_delivery_date",
            "delivery_type", "contact_align", "filter_option", "columns", "active"
        ]
        widgets = {
            "client_name": forms.TextInput(attrs={"class": "form-control"}),
            "client_email": forms.EmailInput(attrs={"class": "form-control"}),
            "number_delivery": forms.NumberInput(attrs={"class": "form-control"}),
            "next_delivery_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "delivery_type": forms.Select(attrs={"class": "form-select"}),
            "contact_align": forms.Select(attrs={"class": "form-select"}),
            "filter_option": forms.SelectMultiple(attrs={"class": "form-select"}),
            "columns": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": '["id", "state", "sale_type", ...]'}),
            "active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
