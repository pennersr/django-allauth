from django.contrib import messages
from django.http import HttpRequest
from django.urls import reverse

from allauth.account import app_settings, signals
from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from allauth.core.internal.httpkit import get_frontend_url
from allauth.utils import build_absolute_uri


def verify_email(request: HttpRequest, email_address: EmailAddress) -> bool:
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
        get_adapter(request).add_message(
            request,
            messages.ERROR,
            "account/messages/email_confirmation_failed.txt",
            {"email": email_address.email},
        )
        return False
    email_address.set_as_primary(conditional=(not app_settings.CHANGE_EMAIL))
    email_address.save()
    if app_settings.CHANGE_EMAIL:
        for instance in EmailAddress.objects.filter(
            user_id=email_address.user_id
        ).exclude(pk=email_address.pk):
            instance.remove()
        emit_email_changed(request, from_email_address, email_address)

    signals.email_confirmed.send(
        sender=EmailAddress,
        request=request,
        email_address=email_address,
    )
    get_adapter(request).add_message(
        request,
        messages.SUCCESS,
        "account/messages/email_confirmed.txt",
        {"email": email_address.email},
    )
    return True


def get_email_verification_url(request: HttpRequest, emailconfirmation) -> str:
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
