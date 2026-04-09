from __future__ import annotations

from django.contrib import messages
from django.http import HttpRequest

from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.internal.flows.reauthentication import (
    raise_if_reauthentication_required,
)
from allauth.core.internal.httpkit import authenticated_user
from allauth.mfa import signals
from allauth.mfa.base.internal.flows import delete_and_cleanup
from allauth.mfa.models import Authenticator
from allauth.mfa.recovery_codes.internal.flows import auto_generate_recovery_codes
from allauth.mfa.totp.internal.auth import TOTP


def activate_totp(
    request: HttpRequest, form
) -> tuple[Authenticator, Authenticator | None]:
    raise_if_reauthentication_required(request)
    user = authenticated_user(request)
    totp_auth = TOTP.activate(user, form.secret).instance
    signals.authenticator_added.send(
        sender=Authenticator,
        request=request,
        user=user,
        authenticator=totp_auth,
    )
    adapter = get_account_adapter(request)
    adapter.add_message(request, messages.SUCCESS, "mfa/messages/totp_activated.txt")
    adapter.send_notification_mail("mfa/email/totp_activated", user)
    rc_auth = auto_generate_recovery_codes(request)
    return totp_auth, rc_auth


def deactivate_totp(request: HttpRequest, authenticator: Authenticator) -> None:
    raise_if_reauthentication_required(request)
    delete_and_cleanup(request, authenticator)
    adapter = get_account_adapter(request)
    adapter.add_message(request, messages.SUCCESS, "mfa/messages/totp_deactivated.txt")
    adapter.send_notification_mail(
        "mfa/email/totp_deactivated", authenticated_user(request)
    )
