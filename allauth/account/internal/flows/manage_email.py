from typing import List, Optional

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
            sender=EmailAddress,
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
    if email_address.pk:
        signals.email_added.send(
            sender=EmailAddress,
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
        assert request.user.is_authenticated  # nosec
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


def emit_email_changed(request, from_email_address, to_email_address) -> None:
    user = to_email_address.user
    signals.email_changed.send(
        sender=EmailAddress,
        request=request,
        user=user,
        from_email_address=from_email_address,
        to_email_address=to_email_address,
    )
    if from_email_address:
        get_adapter().send_notification_mail(
            "account/email/email_changed",
            user,
            context={
                "from_email": from_email_address.email,
                "to_email": to_email_address.email,
            },
            email=from_email_address.email,
        )


def assess_unique_email(email) -> Optional[bool]:
    """
    True -- email is unique
    False -- email is already in use
    None -- email is in use, but we should hide that using email verification.
    """
    from allauth.account.utils import filter_users_by_email

    if not filter_users_by_email(email):
        # All good.
        return True
    elif not app_settings.PREVENT_ENUMERATION:
        # Fail right away.
        return False
    elif (
        app_settings.EMAIL_VERIFICATION
        == app_settings.EmailVerificationMethod.MANDATORY
    ):
        # In case of mandatory verification and enumeration prevention,
        # we can avoid creating a new account with the same (unverified)
        # email address, because we are going to send an email anyway.
        assert app_settings.PREVENT_ENUMERATION  # nosec
        return None
    elif app_settings.PREVENT_ENUMERATION == "strict":
        # We're going to be strict on enumeration prevention, and allow for
        # this email address to pass even though it already exists. In this
        # scenario, you can signup multiple times using the same email
        # address resulting in multiple accounts with an unverified email.
        return True
    else:
        assert app_settings.PREVENT_ENUMERATION is True  # nosec
        # Conflict. We're supposed to prevent enumeration, but we can't
        # because that means letting the user in, while emails are required
        # to be unique. In this case, uniqueness takes precedence over
        # enumeration prevention.
        return False


def list_email_addresses(request, user) -> List[EmailAddress]:
    addresses = list(EmailAddress.objects.filter(user=user))
    if app_settings.EMAIL_VERIFICATION_BY_CODE_ENABLED:
        from allauth.account.internal.flows.email_verification_by_code import (
            get_pending_verification,
        )

        verification, _ = get_pending_verification(request, peek=True)
        if verification and verification.email_address.user_id == user.pk:
            addresses.append(verification.email_address)

    return addresses
