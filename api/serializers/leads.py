from rest_framework import serializers
from propertydata.models import Foreclosure

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Foreclosure
        fields = [
            'id', 
            'CLID', 
            'address', 
            'sale_price', 
            'possible_surplus',
            'fcl_final_judgment',
            # add more fields that are safe to expose
        ]