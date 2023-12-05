from allauth.usersessions import app_settings
from allauth.usersessions.models import UserSession


class UserSessionsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if app_settings.TRACK_ACTIVITY:
            UserSession.objects.create_from_request(request)
        response = self.get_response(request)
        return response
