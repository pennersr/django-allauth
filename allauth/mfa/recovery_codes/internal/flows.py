from typing import Optional

from django.contrib import messages

from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.internal.flows.reauthentication import (
    raise_if_reauthentication_required,
)
from allauth.mfa import app_settings, signals
from allauth.mfa.models import Authenticator
from allauth.mfa.recovery_codes.internal.auth import RecoveryCodes


def can_generate_recovery_codes(user) -> bool:
    return (
        Authenticator.objects.filter(user=user)
        .exclude(type=Authenticator.Type.RECOVERY_CODES)
        .exists()
    )


def generate_recovery_codes(request) -> Authenticator:
    raise_if_reauthentication_required(request)
    Authenticator.objects.filter(
        user=request.user, type=Authenticator.Type.RECOVERY_CODES
    ).delete()
    rc_auth = RecoveryCodes.activate(request.user)
    authenticator = rc_auth.instance
    adapter = get_account_adapter(request)
    adapter.add_message(
        request, messages.SUCCESS, "mfa/messages/recovery_codes_generated.txt"
    )
    signals.authenticator_reset.send(
        sender=Authenticator,
        request=request,
        user=request.user,
        authenticator=authenticator,
    )
    adapter.send_notification_mail("mfa/email/recovery_codes_generated", request.user)
    return authenticator


def view_recovery_codes(request) -> Optional[Authenticator]:
    authenticator = Authenticator.objects.filter(
        user=request.user,
        type=Authenticator.Type.RECOVERY_CODES,
    ).first()
    if not authenticator:
        return None
    raise_if_reauthentication_required(request)
    return authenticator


def auto_generate_recovery_codes(request) -> Optional[Authenticator]:
    """Automatically (implicitly) setup recovery codes when another
    authenticator is setup for. As this is part of setting up another (primary)
    authenticator, we do not send a notification email in this case.
    """
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
    adapter = get_account_adapter(request)
    adapter.add_message(
        request, messages.SUCCESS, "mfa/messages/recovery_codes_generated.txt"
    )
    return rc.instance
