from http import HTTPStatus
from unittest.mock import ANY

from django.urls import reverse

import pytest
from pytest_django.asserts import assertTemplateUsed

from allauth import app_settings as allauth_settings
from allauth.account.adapter import DefaultAccountAdapter, get_adapter
from allauth.account.authentication import get_authentication_records
from allauth.account.decorators import reauthentication_required
from allauth.account.models import EmailAddress
from allauth.core.exceptions import ReauthenticationRequired


class ReauthenticationRequiredAdapter(DefaultAccountAdapter):
    def is_reauthentication_required(self, *, app, **kwargs):
        return app == "allauth.account"


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
    assert {m["url"] for m in methods} == set(map(reverse, expected_method_urlnames))
    for urlname in ["account_reauthenticate", "mfa_reauthenticate"]:
        if urlname == "mfa_reauthenticate" and not allauth_settings.MFA_ENABLED:
            continue
        resp = client.get(f"{reverse(urlname)}?next=/foo")
        if urlname in expected_method_urlnames:
            assert resp.status_code == HTTPStatus.OK
        else:
            assert resp.status_code == HTTPStatus.FOUND
            assert "next=%2Ffoo" in resp["location"]


def test_reauthentication(settings, auth_client, user, user_password):
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
    assert resp.status_code == HTTPStatus.FOUND
    resp = auth_client.post(
        reverse("account_email"),
        {"action_add": "", "email": "john3@example.org"},
    )
    assert resp["location"].startswith(reverse("account_email"))
    methods = get_authentication_records(resp.wsgi_request, user)
    assert methods[-1] == {
        "method": "password",
        "at": ANY,
        "reauthenticated": True,
    }


def test_reauthentication_required_decorator_is_enabled_by_default(settings, rf, user):
    settings.ACCOUNT_REAUTHENTICATION_REQUIRED = False
    request = rf.post("/")
    request.user = user
    request.session = {}

    @reauthentication_required
    def view(request):
        raise AssertionError("The protected view must not be called")

    with pytest.raises(ReauthenticationRequired):
        view(request)


def test_adapter_can_require_reauthentication(settings, auth_client):
    settings.ACCOUNT_REAUTHENTICATION_REQUIRED = False
    settings.ACCOUNT_ADAPTER = (
        "tests.apps.account.test_reauthentication." "ReauthenticationRequiredAdapter"
    )

    resp = auth_client.post(
        reverse("account_email"),
        {"action_add": "", "email": "reauthenticate@example.org"},
    )

    assert not EmailAddress.objects.filter(email="reauthenticate@example.org").exists()
    assert resp["location"].startswith(reverse("account_reauthenticate"))
