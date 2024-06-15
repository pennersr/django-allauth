from typing import Optional, Tuple

from django.contrib import messages

from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.internal.flows.reauthentication import (
    raise_if_reauthentication_required,
)
from allauth.mfa import signals, webauthn
from allauth.mfa.internal.flows.recovery_codes import (
    auto_generate_recovery_codes,
)
from allauth.mfa.models import Authenticator


def add_authenticator(
    request, name: str, authenticator_data: str, passwordless: bool
) -> Tuple[Authenticator, Optional[Authenticator]]:
    auth = webauthn.WebAuthn.add(
        request.user,
        name,
        authenticator_data,
        passwordless,
    ).instance
    signals.authenticator_added.send(
        sender=Authenticator,
        request=request,
        user=request.user,
        authenticator=auth,
    )
    adapter = get_account_adapter(request)
    adapter.add_message(request, messages.SUCCESS, "mfa/messages/webauthn_added.txt")
    rc_auth = auto_generate_recovery_codes(request)
    return auth, rc_auth


def remove_authenticator(request, authenticator: Authenticator):
    raise_if_reauthentication_required(request)
    rc_auth = Authenticator.objects.delete_and_cleanup(authenticator)
    for auth in [authenticator, rc_auth]:
        signals.authenticator_removed.send(
            sender=Authenticator,
            request=request,
            user=request.user,
            authenticator=authenticator,
        )
    adapter = get_account_adapter(request)
    adapter.add_message(request, messages.SUCCESS, "mfa/messages/webauthn_removed.txt")
    # FIXME:
    # adapter.send_notification_mail("mfa/email/totp_deactivated", request.user)
