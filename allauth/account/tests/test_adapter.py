from django.http import HttpResponseRedirect
from django.urls import reverse

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.app_settings import (
    EmailVerificationMethod,
)
from allauth.core.exceptions import ImmediateHttpResponse


class PreLoginRedirectAccountAdapter(DefaultAccountAdapter):
    def pre_login(self, *args, **kwargs):
        raise ImmediateHttpResponse(HttpResponseRedirect("/foo"))


class CustomAccountEmailVerificationAdapter(DefaultAccountAdapter):
    def get_email_verification_method(self, login):
        if login.user.email == "mandatory@example.com":
            return EmailVerificationMethod.MANDATORY
        return EmailVerificationMethod.OPTIONAL


def test_adapter_pre_login(settings, user, user_password, client):
    settings.ACCOUNT_ADAPTER = (
        "allauth.account.tests.test_adapter.PreLoginRedirectAccountAdapter"
    )
    resp = client.post(
        reverse("account_login"),
        {"login": user.username, "password": user_password},
    )
    assert resp.status_code == 302
    assert resp["location"] == "/foo"
