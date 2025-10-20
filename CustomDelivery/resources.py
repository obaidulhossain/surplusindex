from import_export import resources
from propertydata.models import *
from .models import CustomExportOptions
class DynamicDeliveryResource(resources.ModelResource):
    """
    A resource class that builds columns dynamically based on the client's export template.
    """
