from typing import List, Optional, Tuple

from django.contrib import messages
from django.contrib.auth.base_user import AbstractBaseUser
from django.http import HttpRequest

from allauth.account import app_settings, signals
from allauth.account.adapter import get_adapter
from allauth.account.internal.flows.reauthentication import (
    raise_if_reauthentication_required,
)
from allauth.account.internal.userkit import user_email
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
    if email_address.pk:
        signals.email_added.send(
            sender=EmailAddress,
            request=request,
            user=request.user,
            email_address=email_address,
        )


def can_mark_as_primary(email_address: EmailAddress) -> bool:
    if not email_address.pk:
        return False
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


def emit_email_changed(
    request: HttpRequest,
    from_email_address: Optional[EmailAddress],
    to_email_address: EmailAddress,
) -> None:
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


def assess_unique_email(
    email: str, user: Optional[AbstractBaseUser] = None
) -> Optional[bool]:
    """
    True -- email is unique
    False -- email is already in use
    None -- email is in use, but we should hide that using email verification.
    """
    from allauth.account.utils import filter_users_by_email

    if not app_settings.UNIQUE_EMAIL:
        return True

    users_with_email = filter_users_by_email(email)
    if user:
        users_with_email = [u for u in users_with_email if u.pk != user.pk]
    conflict = len(users_with_email) > 0
    if not conflict:
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


def list_email_addresses(
    request: HttpRequest, user: AbstractBaseUser
) -> List[EmailAddress]:
    addresses = list(EmailAddress.objects.filter(user_id=user.pk))
    if (
        app_settings.EMAIL_VERIFICATION_BY_CODE_ENABLED
        and request.user.is_authenticated
    ):
        from allauth.account.internal.flows.email_verification_by_code import (
            EmailVerificationProcess,
        )

        process = EmailVerificationProcess.resume(request)
        if process:
            email_address = process.email_address
            if email_address.user_id == user.pk:
                addresses.append(email_address)

    return addresses


def email_already_exists(
    email: str, user: Optional[AbstractBaseUser] = None, always_raise: bool = False
) -> Tuple[str, bool]:
    """
    Throws a validation error (if allowed by enumeration prevention rules).
    Returns a tuple of [email, already_exists].
    """
    adapter = get_adapter()
    assessment = assess_unique_email(email, user=user)
    if assessment is True:
        # No conflict
        already_exists = False
    elif assessment is False:
        # Fail right away.
        raise adapter.validation_error("email_taken")
    else:
        assert assessment is None  # nosec
        already_exists = True
    email = adapter.validate_unique_email(email)
    if already_exists and always_raise:
        raise adapter.validation_error("email_taken")
    return (email, already_exists)


def sync_user_email_address(user: AbstractBaseUser) -> Optional[EmailAddress]:
    """
    Keep user.email in sync with user.emailaddress_set.

    Under some circumstances the user.email may not have ended up as
    an EmailAddress record, e.g. in the case of manually created admin
    users.
    """
    email = user_email(user)
    if email:
        return sync_email_address(user, email)
    return None


def sync_email_address(user: AbstractBaseUser, email: str) -> Optional[EmailAddress]:
    if not EmailAddress.objects.filter(user_id=user.pk, email=email).exists():
        # get_or_create() to gracefully handle races
        address, _ = EmailAddress.objects.get_or_create(
            user=user, email=email, defaults={"primary": False, "verified": False}
        )
    else:
        address = None
    return address
