from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.utils.timezone import now

def get_logged_in_users():
    sessions = Session.objects.filter(expire_date__gte=now())  # Get non-expired sessions
    user_ids = []

    for session in sessions:
        data = session.get_decoded()  # Decode session data
        user_id = data.get('_auth_user_id')
        if user_id:
            user_ids.append(user_id)

    # Query all User objects for the active user IDs
    logged_in_users = User.objects.filter(id__in=user_ids)
    return logged_in_users
