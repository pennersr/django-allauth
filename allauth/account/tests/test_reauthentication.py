from django.urls import reverse

import pytest

from allauth.account.adapter import get_adapter


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
    user = user_factory(with_totp=with_totp, password=None if with_password else "!")
    assert user.has_usable_password() == with_password
    client.force_login(user)
    methods = get_adapter().get_reauthentication_methods(user)
    assert len(methods) == len(expected_method_urlnames)
    assert set([m["url"] for m in methods]) == set(
        map(reverse, expected_method_urlnames)
    )
    for urlname in ["account_reauthenticate", "mfa_reauthenticate"]:
        resp = client.get(reverse(urlname) + "?next=/foo")
        if urlname in expected_method_urlnames:
            assert resp.status_code == 200
        else:
            assert resp.status_code == 302
            assert "next=%2Ffoo" in resp["location"]
