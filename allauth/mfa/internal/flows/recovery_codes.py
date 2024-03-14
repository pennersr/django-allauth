from django.contrib import messages

from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.mfa import signals
from allauth.mfa.models import Authenticator
from allauth.mfa.recovery_codes import RecoveryCodes


def generate_recovery_codes(request):
    Authenticator.objects.filter(
        user=request.user, type=Authenticator.Type.RECOVERY_CODES
    ).delete()
    rc_auth = RecoveryCodes.activate(request.user)
    adapter = get_account_adapter(request)
    adapter.add_message(
        request, messages.SUCCESS, "mfa/messages/recovery_codes_generated.txt"
    )
    signals.authenticator_reset.send(
        sender=Authenticator, user=request.user, authenticator=rc_auth.instance
    )
    adapter.send_notification_mail("mfa/email/recovery_codes_generated", request.user)
    return rc_auth.instance
