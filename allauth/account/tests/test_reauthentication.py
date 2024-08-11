from unittest.mock import ANY

from django.urls import reverse

import pytest
from pytest_django.asserts import assertTemplateUsed

from allauth import app_settings as allauth_settings
from allauth.account.adapter import get_adapter
from allauth.account.authentication import AUTHENTICATION_METHODS_SESSION_KEY


@pytest.mark.parametrize(
    "with_totp,with_password,expected_method_urlnames",
    [
        (False, True, ["account_reauthenticate"]),
        (True, True, ["account_reauthenticate", "mfa_reauthenticate"]),
        (True, False, ["mfa_reauthenticate"]),
    ],
)
def test_user_with_mfa_only(
    user_factory, with_totp, with_password, expected_method_urlnames, client
):
    if not allauth_settings.MFA_ENABLED and with_totp:
        return
    user = user_factory(with_totp=with_totp, password=None if with_password else "!")
    assert user.has_usable_password() == with_password
    client.force_login(user)
    methods = get_adapter().get_reauthentication_methods(user)
    assert len(methods) == len(expected_method_urlnames)
    assert set([m["url"] for m in methods]) == set(
        map(reverse, expected_method_urlnames)
    )
    for urlname in ["account_reauthenticate", "mfa_reauthenticate"]:
        if urlname == "mfa_reauthenticate" and not allauth_settings.MFA_ENABLED:
            continue
        resp = client.get(reverse(urlname) + "?next=/foo")
        if urlname in expected_method_urlnames:
            assert resp.status_code == 200
        else:
            assert resp.status_code == 302
            assert "next=%2Ffoo" in resp["location"]


def test_reauthentication(settings, auth_client, user_password):
    settings.ACCOUNT_REAUTHENTICATION_REQUIRED = True
    resp = auth_client.post(
        reverse("account_email"),
        {"action_add": "", "email": "john3@example.org"},
    )
    assert resp["location"].startswith(reverse("account_reauthenticate"))
    resp = auth_client.get(reverse("account_reauthenticate"))
    assertTemplateUsed(resp, "account/reauthenticate.html")
    resp = auth_client.post(
        reverse("account_reauthenticate"), data={"password": user_password}
    )
    assert resp.status_code == 302
    resp = auth_client.post(
        reverse("account_email"),
        {"action_add": "", "email": "john3@example.org"},
    )
    assert resp["location"].startswith(reverse("account_email"))
    methods = auth_client.session[AUTHENTICATION_METHODS_SESSION_KEY]
    assert methods[-1] == {"method": "password", "at": ANY, "reauthenticated": True}
