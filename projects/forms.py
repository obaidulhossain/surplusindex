from django import forms
from propertydata.models import *
from django.forms import ModelForm
from django.forms.widgets import SelectDateWidget, TextInput


class ForeclosureForm(forms.ModelForm):
    class Meta:
        model = Foreclosure
#        fields = '__all__'  # Or specify the fields you want to include
        fields = ['state','county','case_number','case_number_ext','court_name','case_type','property', 'case_status', 'plaintiff','defendant', 'sale_date','sale_type','sale_status','fcl_final_judgment','sale_price','possible_surplus','verified_surplus','surplus_status','comment']

        widgets = {
            'sale_date': SelectDateWidget(), # For Date fields
            'case_number': TextInput(attrs={'list': 'case_number_list'}), # Datalist

            # Initially hidden fields or custom widgets for ManyToMany fields
            # that will be populated via AJAX:
            'property': forms.SelectMultiple(attrs={'class': 'hidden'}),  # Or HiddenInput
            'plaintiff': forms.SelectMultiple(attrs={'class': 'hidden'}),
            'defendant': forms.SelectMultiple(attrs={'class': 'hidden'}),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize ManyToMany fields with empty querysets
        self.fields['property'].queryset = Property.objects.none()
        self.fields['plaintiff'].queryset = ForeclosingEntity.objects.none()
        self.fields['defendant'].queryset = Contact.objects.none()


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = '__all__' # Customize as needed

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = '__all__' # Customize as needed

class ForeclosingEntityForm(forms.ModelForm):
    class Meta:
        model = ForeclosingEntity
        fields = '__all__' # Customize as needed













# class ForeclosureModelForm(forms.ModelForm):
#     class Meta:
#         model = Foreclosure
#         fields = ['id','state','county','case_number','case_number_ext','court_name','case_type','case_status','sale_date','sale_type','sale_status','fcl_final_judgment','sale_price','possible_surplus','verified_surplus','surplus_status','comment']




