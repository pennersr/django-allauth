import pytest

from allauth.headless.constants import Client, Flow


@pytest.mark.parametrize("trust", [False, True])
def test_auth_unverified_email_and_mfa(
    client,
    user_with_totp,
    user_password,
    settings_impacting_urls,
    totp_validation_bypass,
    headless_reverse,
    headless_client,
    trust,
):
    with settings_impacting_urls(
        ACCOUNT_LOGIN_METHODS={"email"},
        ACCOUNT_EMAIL_VERIFICATION="mandatory",
        ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION=True,
        MFA_TRUST_ENABLED=True,
    ):
        # Login
        resp = client.post(
            headless_reverse("headless:account:login"),
            data={
                "email": user_with_totp.email,
                "password": user_password,
            },
            content_type="application/json",
        )

        # TOTP is the next stage
        assert resp.status_code == 401
        data = resp.json()
        assert [f for f in data["data"]["flows"] if f["id"] == Flow.MFA_AUTHENTICATE][
            0
        ]["is_pending"]
        with totp_validation_bypass():
            resp = client.post(
                headless_reverse("headless:mfa:authenticate"),
                data={"code": "bad"},
                content_type="application/json",
            )

        if headless_client == Client.APP:
            # App client does not support trust
            assert resp.status_code == 200
        else:
            # Trust stage is pending
            assert resp.status_code == 401
            data = resp.json()
            assert [f for f in data["data"]["flows"] if f["id"] == Flow.MFA_TRUST][0][
                "is_pending"
            ]

            # Indicate trust Y/N
            resp = client.post(
                headless_reverse("headless:mfa:trust"),
                data={"trust": trust},
                content_type="application/json",
            )

            # Logout
            assert resp.status_code == 200
            resp = client.delete(
                headless_reverse("headless:account:current_session"),
            )
            assert resp.status_code == 401

            # Login
            resp = client.post(
                headless_reverse("headless:account:login"),
                data={
                    "email": user_with_totp.email,
                    "password": user_password,
                },
                content_type="application/json",
            )

            # Trust used?
            assert resp.status_code == (200 if trust else 401)
