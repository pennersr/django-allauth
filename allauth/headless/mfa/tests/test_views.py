from allauth.account.models import EmailAddress, get_emailconfirmation_model
from allauth.headless.constants import Flow
from allauth.mfa.models import Authenticator


def test_auth_unverified_email_and_mfa(
    client,
    user_factory,
    password_factory,
    settings,
    totp_validation_bypass,
    headless_reverse,
    headless_client,
):
    settings.ACCOUNT_AUTHENTICATION_METHOD = "email"
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    password = password_factory()
    user = user_factory(email_verified=False, password=password, with_totp=True)
    resp = client.post(
        headless_reverse("headless:account:login"),
        data={
            "email": user.email,
            "password": password,
        },
        content_type="application/json",
    )
    assert resp.status_code == 401
    data = resp.json()
    assert [f for f in data["data"]["flows"] if f["id"] == Flow.VERIFY_EMAIL][0][
        "is_pending"
    ]
    emailaddress = EmailAddress.objects.filter(user=user, verified=False).get()
    key = get_emailconfirmation_model().create(emailaddress).key
    resp = client.post(
        headless_reverse("headless:account:verify_email"),
        data={"key": key},
        content_type="application/json",
    )
    assert resp.status_code == 401
    flows = [
        {"id": "login"},
        {"id": "login_by_code"},
        {"id": "signup"},
    ]
    if headless_client == "browser":
        flows.append(
            {
                "id": "provider_redirect",
                "providers": ["dummy", "openid_connect", "openid_connect"],
            }
        )
    flows.append({"id": "provider_token", "providers": ["dummy"]})
    flows.append(
        {
            "id": "mfa_authenticate",
            "is_pending": True,
        }
    )

    assert resp.json() == {
        "data": {"flows": flows},
        "meta": {"is_authenticated": False},
        "status": 401,
    }
    resp = client.post(
        headless_reverse("headless:mfa:authenticate"),
        data={"code": "bad"},
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert resp.json() == {
        "status": 400,
        "errors": [
            {"message": "Incorrect code.", "code": "incorrect_code", "param": "code"}
        ],
    }

    with totp_validation_bypass():
        resp = client.post(
            headless_reverse("headless:mfa:authenticate"),
            data={"code": "bad"},
            content_type="application/json",
        )
    assert resp.status_code == 200


def test_get_recovery_codes_requires_reauth(
    auth_client, user_with_recovery_codes, headless_reverse
):
    rc = Authenticator.objects.get(
        type=Authenticator.Type.RECOVERY_CODES, user=user_with_recovery_codes
    )
    resp = auth_client.get(headless_reverse("headless:mfa:manage_recovery_codes"))
    assert resp.status_code == 401
    data = resp.json()
    assert data["meta"]["is_authenticated"]
    resp = auth_client.post(
        headless_reverse("headless:mfa:reauthenticate"),
        data={"code": rc.wrap().get_unused_codes()[0]},
        content_type="application/json",
    )
    assert resp.status_code == 200


def test_get_recovery_codes(
    auth_client,
    user_with_recovery_codes,
    headless_reverse,
    reauthentication_bypass,
):
    with reauthentication_bypass():
        resp = auth_client.get(headless_reverse("headless:mfa:manage_recovery_codes"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["data"]["type"] == "recovery_codes"
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
    assert resp.status_code == 404
    with reauthentication_bypass():
        resp = auth_client.post(
            headless_reverse("headless:mfa:manage_recovery_codes"),
            content_type="application/json",
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["data"]["type"] == "recovery_codes"
    assert len(data["data"]["unused_codes"]) == 10


def test_get_totp_not_active(
    auth_client,
    user,
    headless_reverse,
):
    resp = auth_client.get(headless_reverse("headless:mfa:manage_totp"))
    assert resp.status_code == 404
    data = resp.json()
    assert len(data["meta"]["secret"]) == 32


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


def test_activate_totp(
    auth_client,
    user,
    headless_reverse,
    reauthentication_bypass,
    settings,
    totp_validation_bypass,
):
    with reauthentication_bypass():
        with totp_validation_bypass():
            resp = auth_client.post(
                headless_reverse("headless:mfa:manage_totp"),
                data={"code": "42"},
                content_type="application/json",
            )
    assert resp.status_code == 200
    assert Authenticator.objects.filter(
        user=user, type=Authenticator.Type.TOTP
    ).exists()
    data = resp.json()
    assert data["data"]["type"] == "totp"
    assert isinstance(data["data"]["created_at"], float)
    assert data["data"]["last_used_at"] is None
