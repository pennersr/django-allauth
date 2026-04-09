from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.base_user import AbstractBaseUser
from django.http import HttpRequest

from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.internal.flows.reauthentication import (
    raise_if_reauthentication_required,
)
from allauth.mfa import app_settings, signals
from allauth.mfa.models import Authenticator
from allauth.mfa.recovery_codes.internal.auth import RecoveryCodes


def can_generate_recovery_codes(user: AbstractBaseUser) -> bool:
    return (
        Authenticator.objects.filter(user_id=user.pk)
        .exclude(type=Authenticator.Type.RECOVERY_CODES)
        .exists()
    )


def generate_recovery_codes(request: HttpRequest) -> Authenticator:
    raise_if_reauthentication_required(request)
    assert request.user.is_authenticated  # nosec
    Authenticator.objects.filter(
        user=request.user, type=Authenticator.Type.RECOVERY_CODES
    ).delete()
    rc_auth = RecoveryCodes.activate(request.user)
    authenticator = rc_auth.instance
    add_codes_generated_message(request)
    signals.authenticator_reset.send(
        sender=Authenticator,
        request=request,
        user=request.user,
        authenticator=authenticator,
    )
    adapter = get_account_adapter(request)
    adapter.send_notification_mail("mfa/email/recovery_codes_generated", request.user)
    return authenticator


def view_recovery_codes(request: HttpRequest) -> tuple[RecoveryCodes | None, bool]:
    if not request.user.is_authenticated:
        return None, False
    authenticator = Authenticator.objects.filter(
        user=request.user,
        type=Authenticator.Type.RECOVERY_CODES,
    ).first()
    if not authenticator:
        return None, False
    raise_if_reauthentication_required(request)
    wrapper = authenticator.wrap()
    did_view = wrapper.did_view
    if not did_view:
        wrapper.mark_as_viewed()
    can_view = (not app_settings.RECOVERY_CODES_SHOW_ONCE) or not did_view
    return wrapper, can_view


def auto_generate_recovery_codes(request: HttpRequest) -> Authenticator | None:
    """Automatically (implicitly) setup recovery codes when another
    authenticator is setup for. As this is part of setting up another (primary)
    authenticator, we do not send a notification email in this case.
    """
    if not request.user.is_authenticated:
        return None
    if Authenticator.Type.RECOVERY_CODES not in app_settings.SUPPORTED_TYPES:
        return None
    has_rc = Authenticator.objects.filter(
        user=request.user, type=Authenticator.Type.RECOVERY_CODES
    ).exists()
    if has_rc:
        return None
    rc = RecoveryCodes.activate(request.user)
    signals.authenticator_added.send(
        sender=Authenticator,
        request=request,
        user=request.user,
        authenticator=rc.instance,
    )
    add_codes_generated_message(request)
    return rc.instance


def add_codes_generated_message(request: HttpRequest) -> None:
    adapter = get_account_adapter(request)
    adapter.add_message(
        request,
        messages.WARNING if app_settings.RECOVERY_CODES_SHOW_ONCE else messages.SUCCESS,
        "mfa/messages/recovery_codes_generated.txt",
        message_context={
            "MFA_RECOVERY_CODES_SHOW_ONCE": app_settings.RECOVERY_CODES_SHOW_ONCE
        },
    )
