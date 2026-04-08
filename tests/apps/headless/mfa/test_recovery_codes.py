from http import HTTPStatus

import pytest

from allauth.mfa.models import Authenticator


def test_get_recovery_codes_requires_reauth(
    auth_client, user_with_recovery_codes, headless_reverse
):
    rc = Authenticator.objects.get(
        type=Authenticator.Type.RECOVERY_CODES, user=user_with_recovery_codes
    )
    resp = auth_client.get(headless_reverse("headless:mfa:manage_recovery_codes"))
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    data = resp.json()
    assert data["meta"]["is_authenticated"]
    resp = auth_client.post(
        headless_reverse("headless:mfa:reauthenticate"),
        data={"code": rc.wrap().get_unused_codes()[0]},
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.OK


@pytest.mark.parametrize("show_once", [False, True])
def test_get_recovery_codes(
    auth_client,
    user_with_recovery_codes,
    headless_reverse,
    reauthentication_bypass,
    show_once,
    settings,
):
    settings.MFA_RECOVERY_CODES_SHOW_ONCE = show_once
    with reauthentication_bypass():
        for attempt in range(2):
            resp = auth_client.get(
                headless_reverse("headless:mfa:manage_recovery_codes")
            )
            assert resp.status_code == HTTPStatus.OK
            data = resp.json()
            assert data["data"]["type"] == "recovery_codes"
            if show_once and attempt == 1:
                assert "unused_codes" not in data["data"]
            else:
                assert len(data["data"]["unused_codes"]) == 10

    with reauthentication_bypass():
        resp = auth_client.get(headless_reverse("headless:mfa:authenticators"))
    data = resp.json()
    assert len(data["data"]) == 2
    rc = [autor for autor in data["data"] if autor["type"] == "recovery_codes"][0]
    assert "unused_codes" not in rc


def test_generate_recovery_codes(
    auth_client,
    user_with_totp,
    headless_reverse,
    reauthentication_bypass,
):
    with reauthentication_bypass():
        resp = auth_client.get(headless_reverse("headless:mfa:manage_recovery_codes"))
    assert resp.status_code == HTTPStatus.NOT_FOUND
    with reauthentication_bypass():
        resp = auth_client.post(
            headless_reverse("headless:mfa:manage_recovery_codes"),
            content_type="application/json",
        )
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data["data"]["type"] == "recovery_codes"
    assert len(data["data"]["unused_codes"]) == 10
