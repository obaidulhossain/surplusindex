from django.forms import ModelForm
from django import forms
from .models import *

class AddPropertyForm(ModelForm ):
    class Meta:
        model = Property
        # fields = '__all__'
        fields = ["parcel", "state", "county", "house_number", "road_name", "road_type", "direction", "apt_unit", "extention", "city", "zip_code"]


class AddContactForm(ModelForm):
    class Meta:
        model = Contact
        fields = '__all__'






class ForeclosureForm(forms.ModelForm):
    class Meta:
        model = Foreclosure
        fields = [
            'state', 'county', 'case_number', 'case_number_ext', 'court_name', 'case_type', 'property',
            'case_status', 'plaintiff', 'defendant', 'sale_date', 'sale_type', 'sale_status',
            'fcl_final_judgment', 'sale_price', 'possible_surplus', 'verified_surplus', 'surplus_status', 'comment']
    # Define the widgets for the many-to-many fields
    property = forms.ModelMultipleChoiceField(queryset=Property.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    plaintiff = forms.ModelMultipleChoiceField(queryset=Contact.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    defendant = forms.ModelMultipleChoiceField(queryset=Contact.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)