from django.dispatch import Signal

from allauth.account import app_settings

from .models import UserSession


# Emitted when the client (e.g. browser) of a session changes.
# Arguments:
# - request: HttpRequest
# - from_session: UserSession
# - to_session: UserSession
session_client_changed = Signal()


def on_user_logged_in(sender, **kwargs) -> None:
    request = kwargs["request"]
    UserSession.objects.purge_and_list(request.user)
    UserSession.objects.create_from_request(request)


def on_password_changed(sender, **kwargs) -> None:
    if not app_settings.LOGOUT_ON_PASSWORD_CHANGE:
        request = kwargs["request"]
        UserSession.objects.create_from_request(request)
