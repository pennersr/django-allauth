from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse

from allauth import app_settings as allauth_settings
from allauth.account import signals
from allauth.account.adapter import get_adapter
from allauth.core.internal.httpkit import render_url
from allauth.utils import build_absolute_uri


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


def get_reset_password_url(request):
    if allauth_settings.HEADLESS_ENABLED:
        from allauth.headless import app_settings as headless_settings

        url = headless_settings.FRONTEND_URLS.get("account_reset_password")
        if allauth_settings.HEADLESS_ONLY and not url:
            raise ImproperlyConfigured(
                "settings.HEADLESS_FRONTEND_URLS['account_reset_password']"
            )
        if url:
            return render_url(request, url)
    return build_absolute_uri(request, reverse("account_reset_password"))
