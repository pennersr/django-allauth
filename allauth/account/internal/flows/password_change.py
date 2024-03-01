from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

from allauth.account import app_settings, signals
from allauth.account.adapter import get_adapter


def change_password(user, password):
    get_adapter().set_password(user, password)


def finalize_password_change(request, user):
    logout_on_password_change(request, user)
    adapter = get_adapter(request)
    adapter.add_message(
        request,
        messages.SUCCESS,
        "account/messages/password_changed.txt",
    )
    adapter.send_notification_mail("account/email/password_changed", request.user)
    signals.password_changed.send(
        sender=request.user.__class__,
        request=request,
        user=request.user,
    )


def finalize_password_set(request, user):
    logout_on_password_change(request, user)
    adapter = get_adapter(request)
    adapter.add_message(request, messages.SUCCESS, "account/messages/password_set.txt")
    adapter.send_notification_mail("account/email/password_set", user)
    signals.password_set.send(
        sender=user.__class__,
        request=request,
        user=user,
    )


def logout_on_password_change(request, user):
    # Since it is the default behavior of Django to invalidate all sessions on
    # password change, this function actually has to preserve the session when
    # logout isn't desired.
    if not app_settings.LOGOUT_ON_PASSWORD_CHANGE:
        update_session_auth_hash(request, user)
