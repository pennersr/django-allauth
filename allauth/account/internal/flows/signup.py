from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse

from allauth import app_settings as allauth_settings
from allauth.account.adapter import get_adapter
from allauth.core.internal.httpkit import render_url
from allauth.utils import build_absolute_uri


def send_unknown_account_mail(request, email):
    signup_url = get_signup_url(request)
    context = {
        "request": request,
        "signup_url": signup_url,
    }
    get_adapter().send_mail("account/email/unknown_account", email, context)


def get_signup_url(request):
    if allauth_settings.HEADLESS_ENABLED:
        from allauth.headless import app_settings as headless_settings

        url = headless_settings.FRONTEND_URLS.get("account_signup")
        if allauth_settings.HEADLESS_ONLY and not url:
            raise ImproperlyConfigured(
                "settings.HEADLESS_FRONTEND_URLS['account_signup']"
            )
        if url:
            return render_url(request, url)
    return build_absolute_uri(request, reverse("account_signup"))
