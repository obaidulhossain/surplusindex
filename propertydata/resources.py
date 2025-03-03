# resources.py
from import_export import resources
from .models import *

class ForeclosingEntityResource(resources.ModelResource):
    class Meta:
        model = ForeclosingEntity
        import_id_fields = ('id',)
        exclude = [
            'dba'
            ]

class ForeclosingEntityExportResource(resources.ModelResource):
    class Meta:
        model = ForeclosingEntity
