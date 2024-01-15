from allauth.account import app_settings

from .models import UserSession


def on_user_logged_in(sender, **kwargs):
    request = kwargs["request"]
    UserSession.objects.create_from_request(request)


def on_password_changed(sender, **kwargs):
    if not app_settings.LOGOUT_ON_PASSWORD_CHANGE:
        request = kwargs["request"]
        UserSession.objects.create_from_request(request)
