from django.test import override_settings
from django.urls import reverse

import pytest

from allauth.mfa.middleware import RequireMFAMiddleware


class RequireMFA(RequireMFAMiddleware):
    def mfa_required(self, request):
        return True


new_middleware = [
    "allauth.mfa.tests.test_middleware.RequireMFA",
]


def test_require_mfa_middleware(settings, auth_client):
    with override_settings(
        MIDDLEWARE=settings.MIDDLEWARE + tuple(new_middleware),
    ):
        resp = auth_client.get(
            reverse("account_email"),
        )
        assert resp.status_code == 302
        assert resp["location"] == reverse("mfa_activate_totp")


@pytest.mark.parametrize("url", RequireMFAMiddleware.allowed_urls)
def test_require_mfa_middleware_not_on_allowed_urls(
    settings, auth_client, reauthentication_bypass, url
):
    with override_settings(
        MIDDLEWARE=settings.MIDDLEWARE + tuple(new_middleware),
    ):
        with reauthentication_bypass():
            resp = auth_client.get(
                reverse(url),
            )
            if url == "account_login":
                # for logged-in users a GET to the login page results
                # in a redirect to the profile page
                assert resp.status_code == 302
                # not redirected to MFA setup
                assert resp["location"] != reverse("mfa_activate_totp")
            else:
                # no redirect for allowed urls
                assert resp.status_code == 200


def test_require_mfa_middleware_not_for_user_with_totp(
    auth_client, user_with_totp, user_password
):
    resp = auth_client.get(
        reverse("account_email"),
    )
    # no redirect for a user who has MFA enabled already
    assert resp.status_code == 200


def test_require_mfa_middleware_not_for_unauthenticated_user(client):
    resp = client.get(
        reverse("account_email"),
    )
    # redirect to login-page not MFA setup
    assert resp.status_code == 302
    assert reverse("mfa_activate_totp") not in resp["location"]
