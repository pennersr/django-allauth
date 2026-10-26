from http import HTTPStatus
from unittest.mock import patch

import pytest

from allauth.account.internal.flows.login import record_authentication
from allauth.mfa.models import Authenticator


@pytest.mark.parametrize(
    "code",
    [
        pytest.param("123-456", id="dash"),
        pytest.param("1 23456", id="space"),
        pytest.param(["123456"], id="list"),
        pytest.param(1234.56, id="float"),
        pytest.param({"": "123456"}, id="object"),
    ],
)
def test_reauthenticate_totp_code_reuse_with_alternate_representation(
    auth_client,
    user_with_totp,
    headless_reverse,
    totp_validation_bypass,
    enable_cache,
    request_factory,
    code,
):
    request = request_factory.get("/")
    request.session = auth_client.headless_session()
    record_authentication(
        request, user_with_totp, method="mfa", at=0, reauthenticated=True
    )
    request.session.save()

    with totp_validation_bypass():
        resp = auth_client.post(
            headless_reverse("headless:mfa:reauthenticate"),
            data={"code": "123456"},
            content_type="application/json",
        )
        assert resp.status_code == HTTPStatus.OK

        resp = auth_client.post(
            headless_reverse("headless:mfa:reauthenticate"),
            data={"code": code},
            content_type="application/json",
        )

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json()["errors"] == [
        {"param": "code", "message": "Incorrect code.", "code": "incorrect_code"}
    ]


@pytest.mark.parametrize(
    "code",
    [
        pytest.param("123-456", id="dash"),
        pytest.param("1 23456", id="space"),
        pytest.param(["123456"], id="list"),
        pytest.param(123456, id="integer"),
        pytest.param(1234.56, id="float"),
        pytest.param({"": "123456"}, id="object"),
    ],
)
def test_activate_totp_normalizes_code(
    auth_client,
    user,
    headless_reverse,
    reauthentication_bypass,
    code,
):
    with reauthentication_bypass():
        auth_client.get(headless_reverse("headless:mfa:manage_totp"))
        with patch("allauth.mfa.totp.internal.auth.hotp_value", return_value=123456):
            resp = auth_client.post(
                headless_reverse("headless:mfa:manage_totp"),
                data={"code": code},
                content_type="application/json",
            )

    assert resp.status_code == HTTPStatus.OK
    assert Authenticator.objects.filter(
        user=user, type=Authenticator.Type.TOTP
    ).exists()


@pytest.mark.parametrize("email_verified", [False, True])
def test_get_totp_not_active(auth_client, user, headless_reverse, email_verified):
    resp = auth_client.get(headless_reverse("headless:mfa:manage_totp"))
    if email_verified:
        assert resp.status_code == HTTPStatus.NOT_FOUND
        data = resp.json()
        assert len(data["meta"]["secret"]) == 32
        assert len(data["meta"]["totp_url"]) == 145
    else:
        assert resp.status_code == HTTPStatus.CONFLICT
        assert resp.json() == {
            "status": HTTPStatus.CONFLICT,
            "errors": [
                {
                    "message": "You cannot activate two-factor authentication until you have verified your email address.",
                    "code": "unverified_email",
                }
            ],
        }


def test_get_totp(
    auth_client,
    user_with_totp,
    headless_reverse,
):
    resp = auth_client.get(headless_reverse("headless:mfa:manage_totp"))
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data["data"]["type"] == "totp"
    assert isinstance(data["data"]["created_at"], float)


def test_deactivate_totp(
    auth_client,
    user_with_totp,
    headless_reverse,
    reauthentication_bypass,
):
    with reauthentication_bypass():
        resp = auth_client.delete(headless_reverse("headless:mfa:manage_totp"))
    assert resp.status_code == HTTPStatus.OK
    assert not Authenticator.objects.filter(user=user_with_totp).exists()


def test_deactivate_totp_with_reauthenticate(
    auth_client,
    user_with_totp,
    headless_reverse,
    totp_validation_bypass,
    request_factory,
):
    # Let's ensure the session requires reauthentication by having an old `at`.
    request = request_factory.get("/")
    request.session = auth_client.headless_session()
    record_authentication(
        request, user_with_totp, method="mfa", at=0, reauthenticated=True
    )
    request.session.save()

    # Attempt to deactivate, should not be allowed.
    resp = auth_client.delete(headless_reverse("headless:mfa:manage_totp"))
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    assert resp.json()["data"]["flows"] == [
        {"id": "reauthenticate"},
        {"id": "mfa_reauthenticate", "types": ["totp"]},
    ]
    assert Authenticator.objects.filter(user=user_with_totp).exists()

    # Now, reauthenticate...
    with totp_validation_bypass():
        resp = auth_client.post(
            headless_reverse("headless:mfa:reauthenticate"),
            data={"code": "42"},
            content_type="application/json",
        )
    assert resp.status_code == HTTPStatus.OK

    # ... and try again.
    resp = auth_client.delete(headless_reverse("headless:mfa:manage_totp"))
    assert resp.status_code == HTTPStatus.OK

    # Success
    assert not Authenticator.objects.filter(user=user_with_totp).exists()


@pytest.mark.parametrize("email_verified", [False, True])
def test_activate_totp(
    auth_client,
    user,
    headless_reverse,
    reauthentication_bypass,
    settings,
    totp_validation_bypass,
    email_verified,
):
    with reauthentication_bypass():
        with totp_validation_bypass():
            resp = auth_client.post(
                headless_reverse("headless:mfa:manage_totp"),
                data={"code": "42"},
                content_type="application/json",
            )
    if email_verified:
        assert resp.status_code == HTTPStatus.OK
        assert Authenticator.objects.filter(
            user=user, type=Authenticator.Type.TOTP
        ).exists()
        data = resp.json()
        assert data["data"]["type"] == "totp"
        assert isinstance(data["data"]["created_at"], float)
        assert data["data"]["last_used_at"] is None
    else:
        assert resp.status_code == HTTPStatus.BAD_REQUEST


def test_activate_totp_rate_limit(
    auth_client,
    headless_reverse,
    reauthentication_bypass,
    settings,
    enable_cache,
):
    settings.ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 1
    with reauthentication_bypass():
        auth_client.get(headless_reverse("headless:mfa:manage_totp"))
        for i in range(2):
            is_locked = i >= 1
            resp = auth_client.post(
                headless_reverse("headless:mfa:manage_totp"),
                data={"code": "wrong"},
                content_type="application/json",
            )
            assert resp.status_code == HTTPStatus.BAD_REQUEST
            assert resp.json()["errors"] == [
                (
                    {
                        "param": "code",
                        "message": "Be patient, you are sending too many requests.",
                        "code": "rate_limited",
                    }
                    if is_locked
                    else {
                        "param": "code",
                        "message": "Incorrect code.",
                        "code": "incorrect_code",
                    }
                )
            ]
