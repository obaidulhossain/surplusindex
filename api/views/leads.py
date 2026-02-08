from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.serializers.leads import LeadSerializer
from propertydata.models import Foreclosure

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def leads_list(request):
    """
    Return a list of all available leads for the authenticated user.
    """
    # Example: only leads with sale_price null (available leads)
    leads = Foreclosure.objects.filter(sale_price__isnull=True)[:50]  # limit to 50 for safety
    serializer = LeadSerializer(leads, many=True)
    return Response(serializer.data)