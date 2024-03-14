from django.contrib import messages

from allauth.account import app_settings as account_settings
from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.reauthentication import raise_if_reauthentication_required
from allauth.socialaccount import signals
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.models import SocialAccount


def disconnect(request, account):
    if account_settings.REAUTHENTICATION_REQUIRED:
        raise_if_reauthentication_required(request)

    get_account_adapter().add_message(
        request,
        messages.INFO,
        "socialaccount/messages/account_disconnected.txt",
    )
    provider = account.get_provider()
    account.delete()
    signals.social_account_removed.send(
        sender=SocialAccount, request=request, socialaccount=account
    )
    get_adapter().send_notification_mail(
        "socialaccount/email/account_disconnected",
        request.user,
        context={
            "account": account,
            "provider": provider,
        },
    )
