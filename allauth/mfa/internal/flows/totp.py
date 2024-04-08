from django.contrib import messages

from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.reauthentication import raise_if_reauthentication_required
from allauth.mfa import app_settings, signals, totp
from allauth.mfa.models import Authenticator
from allauth.mfa.recovery_codes import RecoveryCodes


def activate_totp(request, form):
    raise_if_reauthentication_required(request)
    totp_auth = totp.TOTP.activate(request.user, form.secret)
    if Authenticator.Type.RECOVERY_CODES in app_settings.SUPPORTED_TYPES:
        rc_auth = RecoveryCodes.activate(request.user)
    else:
        rc_auth = None
    for auth in [totp_auth, rc_auth]:
        if auth:
            signals.authenticator_added.send(
                sender=Authenticator,
                request=request,
                user=request.user,
                authenticator=auth.instance,
            )
    adapter = get_account_adapter(request)
    adapter.add_message(request, messages.SUCCESS, "mfa/messages/totp_activated.txt")
    adapter.send_notification_mail("mfa/email/totp_activated", request.user)
    return totp_auth


def deactivate_totp(request, authenticator):
    raise_if_reauthentication_required(request)
    authenticator.wrap().deactivate()
    rc_auth = Authenticator.objects.delete_dangling_recovery_codes(authenticator.user)
    for auth in [authenticator, rc_auth]:
        if auth:
            signals.authenticator_removed.send(
                sender=Authenticator,
                request=request,
                user=request.user,
                authenticator=auth,
            )
    adapter = get_account_adapter(request)
    adapter.add_message(request, messages.SUCCESS, "mfa/messages/totp_deactivated.txt")
    adapter.send_notification_mail("mfa/email/totp_deactivated", request.user)
