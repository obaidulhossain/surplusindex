from django.utils.deprecation import MiddlewareMixin
from Admin.utils.threadlocal import set_current_user


class CurrentUserMiddleware(MiddlewareMixin):
    """Middleware to store the current user in thread-local storage for models to access."""
    
    def process_request(self, request):
        set_current_user(request.user)