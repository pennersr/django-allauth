from django.contrib import messages
from django.http import HttpRequest

from allauth.account import app_settings, signals
from allauth.account.adapter import get_adapter
from allauth.account.internal.flows.reauthentication import (
    raise_if_reauthentication_required,
)
from allauth.account.models import EmailAddress


def can_delete_email(email_address: EmailAddress) -> bool:
    adapter = get_adapter()
    return adapter.can_delete_email(email_address)


def delete_email(request: HttpRequest, email_address: EmailAddress) -> bool:
    if app_settings.REAUTHENTICATION_REQUIRED:
        raise_if_reauthentication_required(request)

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


def add_email(request: HttpRequest, form):
    if app_settings.REAUTHENTICATION_REQUIRED:
        raise_if_reauthentication_required(request)

    email_address = form.save(request)
    adapter = get_adapter(request)
    adapter.add_message(
        request,
        messages.INFO,
        "account/messages/email_confirmation_sent.txt",
        {"email": form.cleaned_data["email"]},
    )
    signals.email_added.send(
        sender=request.user.__class__,
        request=request,
        user=request.user,
        email_address=email_address,
    )


def can_mark_as_primary(email_address: EmailAddress):
    return (
        email_address.verified
        or not EmailAddress.objects.filter(
            user=email_address.user, verified=True
        ).exists()
    )


def mark_as_primary(request: HttpRequest, email_address: EmailAddress):
    from allauth.account.utils import emit_email_changed

    if app_settings.REAUTHENTICATION_REQUIRED:
        raise_if_reauthentication_required(request)

    # Not primary=True -- Slightly different variation, don't
    # require verified unless moving from a verified
    # address. Ignore constraint if previous primary email
    # address is not verified.
    success = False
    if not can_mark_as_primary(email_address):
        get_adapter().add_message(
            request,
            messages.ERROR,
            "account/messages/unverified_primary_email.txt",
        )
    else:
        assert request.user.is_authenticated
        from_email_address = EmailAddress.objects.filter(
            user=request.user, primary=True
        ).first()
        email_address.set_as_primary()
        adapter = get_adapter()
        adapter.add_message(
            request,
            messages.SUCCESS,
            "account/messages/primary_email_set.txt",
        )
        emit_email_changed(request, from_email_address, email_address)
        success = True
    return success
