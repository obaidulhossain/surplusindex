# api/views/auth.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """
    Return current authenticated user details.
    """
    user = request.user
    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        # "credits": getattr(user, "Total_credits", 0),
        # "subscription": getattr(user, "subscription_status", None)
    })