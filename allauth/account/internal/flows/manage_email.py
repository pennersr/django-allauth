from django.contrib import messages
from django.urls import reverse

from allauth.account import app_settings, signals
from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from allauth.account.reauthentication import raise_if_reauthentication_required
from allauth.core.internal.httpkit import get_frontend_url
from allauth.utils import build_absolute_uri


def can_delete_email(email_address):
    adapter = get_adapter()
    return adapter.can_delete_email(email_address)


def delete_email(request, email_address):
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


def add_email(request, form):
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


def can_mark_as_primary(email_address):
    return (
        email_address.verified
        or not EmailAddress.objects.filter(
            user=email_address.user, verified=True
        ).exists()
    )


def mark_as_primary(request, email_address):
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


def verify_email(request, email_address):
    """
    Marks the email address as confirmed on the db
    """
    from allauth.account.models import EmailAddress
    from allauth.account.utils import emit_email_changed

    from_email_address = (
        EmailAddress.objects.filter(user_id=email_address.user_id)
        .exclude(pk=email_address.pk)
        .first()
    )
    if not email_address.set_verified(commit=False):
        return False
    email_address.set_as_primary(conditional=(not app_settings.CHANGE_EMAIL))
    email_address.save(update_fields=["verified", "primary"])
    if app_settings.CHANGE_EMAIL:
        for instance in EmailAddress.objects.filter(
            user_id=email_address.user_id
        ).exclude(pk=email_address.pk):
            instance.remove()
        emit_email_changed(request, from_email_address, email_address)
    return True


def get_email_verification_url(request, emailconfirmation):
    """Constructs the email confirmation (activation) url.

    Note that if you have architected your system such that email
    confirmations are sent outside of the request context `request`
    can be `None` here.
    """
    url = get_frontend_url(request, "account_confirm_email", key=emailconfirmation.key)
    if not url:
        url = reverse("account_confirm_email", args=[emailconfirmation.key])
        url = build_absolute_uri(request, url)
    return url
