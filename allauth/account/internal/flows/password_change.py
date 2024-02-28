from django.contrib import messages

from allauth.account import signals
from allauth.account.adapter import get_adapter
from allauth.account.utils import logout_on_password_change


def change_password(user, password):
    get_adapter().set_password(user, password)


def finalize_password_change(request, user):
    logout_on_password_change(request, user)
    adapter = get_adapter(request)
    adapter.add_message(
        request,
        messages.SUCCESS,
        "account/messages/password_changed.txt",
    )
    adapter.send_notification_mail("account/email/password_changed", request.user)
    signals.password_changed.send(
        sender=request.user.__class__,
        request=request,
        user=request.user,
    )


def finalize_password_set(request, user):
    logout_on_password_change(request, user)
    adapter = get_adapter(request)
    adapter.add_message(request, messages.SUCCESS, "account/messages/password_set.txt")
    adapter.send_notification_mail("account/email/password_set", user)
    signals.password_set.send(
        sender=user.__class__,
        request=request,
        user=user,
    )
