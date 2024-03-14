from django.contrib import messages

from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.socialaccount import signals
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.models import SocialAccount


def disconnect(request, account):
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
