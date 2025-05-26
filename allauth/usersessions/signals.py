from django.dispatch import Signal

from allauth.account import app_settings

from .models import UserSession


# Provides the arguments "request", "from_session", "to_session"
session_client_changed = Signal()


def on_user_logged_in(sender, **kwargs):
    request = kwargs["request"]
    UserSession.objects.purge_and_list(request.user)
    UserSession.objects.create_from_request(request)


def on_password_changed(sender, **kwargs):
    if not app_settings.LOGOUT_ON_PASSWORD_CHANGE:
        request = kwargs["request"]
        UserSession.objects.create_from_request(request)
