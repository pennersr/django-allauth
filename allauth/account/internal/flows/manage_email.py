from django.contrib import messages

from allauth.account import signals
from allauth.account.adapter import get_adapter


def can_delete_email(email_address):
    adapter = get_adapter()
    return adapter.can_delete_email(email_address)


def delete_email(request, email_address):
    success = False
    adapter = get_adapter()
    if not can_delete_email(email_address):
        adapter.add_message(
            request,
            messages.ERROR,
            "account/messages/cannot_delete_primary_email.txt",
            {"email": email_address.email},
        )
    else:
        email_address.remove()
        signals.email_removed.send(
            sender=request.user.__class__,
            request=request,
            user=request.user,
            email_address=email_address,
        )
        adapter.add_message(
            request,
            messages.SUCCESS,
            "account/messages/email_deleted.txt",
            {"email": email_address.email},
        )
        adapter.send_notification_mail(
            "account/email/email_deleted",
            request.user,
            {"deleted_email": email_address.email},
        )
        success = True
    return success
