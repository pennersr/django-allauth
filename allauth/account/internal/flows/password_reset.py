from django.contrib import messages

from allauth.account import signals
from allauth.account.adapter import get_adapter


def reset_password(user, password):
    get_adapter().set_password(user, password)


def finalize_password_reset(request, user):
    adapter = get_adapter()
    if user:
        # User successfully reset the password, clear any
        # possible cache entries for all email addresses.
        for email in user.emailaddress_set.all():
            adapter._delete_login_attempts_cached_email(request, email=email.email)

    adapter.add_message(
        request,
        messages.SUCCESS,
        "account/messages/password_changed.txt",
    )
    signals.password_reset.send(
        sender=user.__class__,
        request=request,
        user=user,
    )
    adapter.send_notification_mail("account/email/password_reset", user)
