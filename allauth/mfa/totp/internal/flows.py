from typing import Optional, Tuple

from django.contrib import messages

from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.internal.flows.reauthentication import (
    raise_if_reauthentication_required,
)
from allauth.mfa import signals
from allauth.mfa.base.internal.flows import delete_and_cleanup
from allauth.mfa.models import Authenticator
from allauth.mfa.recovery_codes.internal.flows import auto_generate_recovery_codes
from allauth.mfa.totp.internal.auth import TOTP


def activate_totp(request, form) -> Tuple[Authenticator, Optional[Authenticator]]:
    raise_if_reauthentication_required(request)
    totp_auth = TOTP.activate(request.user, form.secret).instance
    signals.authenticator_added.send(
        sender=Authenticator,
        request=request,
        user=request.user,
        authenticator=totp_auth,
    )
    adapter = get_account_adapter(request)
    adapter.add_message(request, messages.SUCCESS, "mfa/messages/totp_activated.txt")
    adapter.send_notification_mail("mfa/email/totp_activated", request.user)
    rc_auth = auto_generate_recovery_codes(request)
    return totp_auth, rc_auth


def deactivate_totp(request, authenticator: Authenticator) -> None:
    raise_if_reauthentication_required(request)
    delete_and_cleanup(request, authenticator)
    adapter = get_account_adapter(request)
    adapter.add_message(request, messages.SUCCESS, "mfa/messages/totp_deactivated.txt")
    adapter.send_notification_mail("mfa/email/totp_deactivated", request.user)
