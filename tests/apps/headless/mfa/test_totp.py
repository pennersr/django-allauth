import pytest

from allauth.mfa.models import Authenticator


@pytest.mark.parametrize("email_verified", [False, True])
def test_get_totp_not_active(auth_client, user, headless_reverse, email_verified):
    resp = auth_client.get(headless_reverse("headless:mfa:manage_totp"))
    if email_verified:
        assert resp.status_code == 404
        data = resp.json()
        assert len(data["meta"]["secret"]) == 32
        assert len(data["meta"]["totp_url"]) == 145
    else:
        assert resp.status_code == 409
        assert resp.json() == {
            "status": 409,
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
    assert resp.status_code == 200
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
    assert resp.status_code == 200
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
        assert resp.status_code == 200
        assert Authenticator.objects.filter(
            user=user, type=Authenticator.Type.TOTP
        ).exists()
        data = resp.json()
        assert data["data"]["type"] == "totp"
        assert isinstance(data["data"]["created_at"], float)
        assert data["data"]["last_used_at"] is None
    else:
        assert resp.status_code == 400
