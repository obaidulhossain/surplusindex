from django.forms import ModelForm
from .models import Property

class AddPropertyForm(ModelForm ):
    class Meta:
        model = Property
        fields = '__all__'