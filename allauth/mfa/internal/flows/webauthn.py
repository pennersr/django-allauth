from typing import Optional, Tuple

from django.contrib import messages

from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.internal.flows.reauthentication import (
    raise_if_reauthentication_required,
)
from allauth.mfa import signals, webauthn
from allauth.mfa.internal.flows.base import delete_and_cleanup
from allauth.mfa.internal.flows.recovery_codes import (
    auto_generate_recovery_codes,
)
from allauth.mfa.models import Authenticator


def add_authenticator(
    request, name: str, credential: dict
) -> Tuple[Authenticator, Optional[Authenticator]]:
    auth = webauthn.WebAuthn.add(
        request.user,
        name,
        credential,
    ).instance
    signals.authenticator_added.send(
        sender=Authenticator,
        request=request,
        user=request.user,
        authenticator=auth,
    )
    adapter = get_account_adapter(request)
    adapter.add_message(request, messages.SUCCESS, "mfa/messages/webauthn_added.txt")
    adapter.send_notification_mail("mfa/email/webauthn_added", request.user)
    rc_auth = auto_generate_recovery_codes(request)
    return auth, rc_auth


def remove_authenticator(request, authenticator: Authenticator):
    raise_if_reauthentication_required(request)
    delete_and_cleanup(request, authenticator)
    adapter = get_account_adapter(request)
    adapter.add_message(request, messages.SUCCESS, "mfa/messages/webauthn_removed.txt")
    adapter.send_notification_mail("mfa/email/webauthn_removed", request.user)
