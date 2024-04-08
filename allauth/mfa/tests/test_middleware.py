from django.test import override_settings
from django.urls import reverse
from django.utils.http import int_to_base36

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


@pytest.mark.parametrize(
    "url, url_kwargs, expected_status_code",
    [
        ("account_login", None, 302),
        ("account_logout", None, 200),
        ("account_reauthenticate", None, 200),
        ("account_change_password", None, 200),
        ("account_set_password", None, 302),
        ("account_inactive", None, 200),
        ("account_reset_password", None, 200),
        ("account_reset_password_done", None, 200),
        (
            "account_reset_password_from_key",
            {"uidb36": int_to_base36(1234), "key": "abcd1234"},
            200,
        ),
        ("account_reset_password_from_key_done", None, 200),
        ("socialaccount_login_cancelled", None, 200),
        ("socialaccount_login_error", None, 200),
        ("socialaccount_connections", None, 200),
        ("mfa_activate_totp", None, 200),
        ("mfa_index", None, 200),
    ],
)
def test_require_mfa_middleware_not_on_allowed_urls(
    settings,
    auth_client,
    reauthentication_bypass,
    url,
    url_kwargs,
    expected_status_code,
):
    with override_settings(
        MIDDLEWARE=settings.MIDDLEWARE + tuple(new_middleware),
    ):
        with reauthentication_bypass():
            resp = auth_client.get(
                reverse(url, kwargs=url_kwargs),
            )
            assert resp.status_code == expected_status_code
            if expected_status_code == 302:
                assert resp["location"] != reverse("mfa_activate_totp")


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
