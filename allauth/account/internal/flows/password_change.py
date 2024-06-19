from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import AbstractBaseUser
from django.http import HttpRequest

from allauth.account import app_settings, signals
from allauth.account.adapter import get_adapter
from allauth.account.internal.flows.logout import logout


def change_password(user: AbstractBaseUser, password: str) -> None:
    get_adapter().set_password(user, password)


def finalize_password_change(request: HttpRequest, user: AbstractBaseUser) -> bool:
    logged_out = logout_on_password_change(request, user)
    adapter = get_adapter(request)
    adapter.add_message(
        request,
        messages.SUCCESS,
        "account/messages/password_changed.txt",
    )
    adapter.send_notification_mail("account/email/password_changed", user)
    signals.password_changed.send(
        sender=user.__class__,
        request=request,
        user=user,
    )
    return logged_out


def finalize_password_set(request: HttpRequest, user: AbstractBaseUser) -> bool:
    logged_out = logout_on_password_change(request, user)
    adapter = get_adapter(request)
    adapter.add_message(request, messages.SUCCESS, "account/messages/password_set.txt")
    adapter.send_notification_mail("account/email/password_set", user)
    signals.password_set.send(
        sender=user.__class__,
        request=request,
        user=user,
    )
    return logged_out


def logout_on_password_change(request: HttpRequest, user: AbstractBaseUser) -> bool:
    # Since it is the default behavior of Django to invalidate all sessions on
    # password change, this function actually has to preserve the session when
    # logout isn't desired.
    logged_out = True
    if not app_settings.LOGOUT_ON_PASSWORD_CHANGE:
        update_session_auth_hash(request, user)
        logged_out = False
    else:
        logout(request)
    return logged_out
