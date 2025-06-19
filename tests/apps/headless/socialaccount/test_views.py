import json
from http import HTTPStatus
from unittest.mock import patch

from django.urls import reverse

from pytest_django.asserts import assertTemplateUsed

from allauth.account.models import EmailAddress
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.base.constants import AuthProcess


def test_bad_redirect(client, headless_reverse, db, settings):
    settings.HEADLESS_ONLY = False
    resp = client.post(
        headless_reverse("headless:socialaccount:redirect_to_provider"),
        data={
            "provider": "dummy",
            "callback_url": "https://unsafe.org/hack",
            "process": AuthProcess.LOGIN,
        },
    )
    assertTemplateUsed(resp, "socialaccount/authentication_error.html")


def test_valid_redirect(client, headless_reverse, db):
    resp = client.post(
        headless_reverse("headless:socialaccount:redirect_to_provider"),
        data={
            "provider": "dummy",
            "callback_url": "/",
            "process": AuthProcess.LOGIN,
        },
    )
    assert resp.status_code == HTTPStatus.FOUND


def test_unknown_provider_redirect(client, headless_reverse, db, settings):
    resp = client.post(
        headless_reverse("headless:socialaccount:redirect_to_provider"),
        data={
            "provider": "unknown",
            "callback_url": "/",
            "process": AuthProcess.LOGIN,
        },
    )
    if getattr(settings, "HEADLESS_ONLY", False):
        assert resp.status_code == HTTPStatus.FOUND
    else:
        assert resp.status_code == HTTPStatus.OK


def test_manage_providers(auth_client, user, headless_reverse, provider_id):
    account_to_del = SocialAccount.objects.create(
        user=user, provider=provider_id, uid="p123"
    )
    account_to_keep = SocialAccount.objects.create(
        user=user, provider=provider_id, uid="p456"
    )
    resp = auth_client.get(
        headless_reverse("headless:socialaccount:manage_providers"),
    )
    data = resp.json()
    assert data["status"] == HTTPStatus.OK
    assert len(data["data"]) == 2
    resp = auth_client.delete(
        headless_reverse("headless:socialaccount:manage_providers"),
        data={"provider": account_to_del.provider, "account": account_to_del.uid},
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {
        "status": HTTPStatus.OK,
        "data": [
            {
                "display": "Unittest Server",
                "provider": {
                    "client_id": "Unittest client_id",
                    "openid_configuration_url": "https://unittest.example.com/.well-known/openid-configuration",
                    "flows": ["provider_redirect", "provider_token"],
                    "id": provider_id,
                    "name": "Unittest Server",
                },
                "uid": "p456",
            }
        ],
    }
    assert not SocialAccount.objects.filter(pk=account_to_del.pk).exists()
    assert SocialAccount.objects.filter(pk=account_to_keep.pk).exists()


def test_disconnect_bad_request(auth_client, user, headless_reverse, provider_id):
    resp = auth_client.delete(
        headless_reverse("headless:socialaccount:manage_providers"),
        data={"provider": provider_id, "account": "unknown"},
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json() == {
        "status": HTTPStatus.BAD_REQUEST,
        "errors": [{"code": "account_not_found", "message": "Unknown account."}],
    }


def test_disconnect_not_allowed(auth_client, user, headless_reverse, provider_id):
    user.set_unusable_password()
    user.save(update_fields=["password"])
    auth_client.force_login(user)
    account = SocialAccount.objects.create(user=user, uid="123", provider=provider_id)
    resp = auth_client.delete(
        headless_reverse("headless:socialaccount:manage_providers"),
        data={"provider": provider_id, "account": account.uid},
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json() == {
        "status": HTTPStatus.BAD_REQUEST,
        "errors": [
            {"code": "no_password", "message": "Your account has no password set up."}
        ],
    }


def test_valid_token(client, headless_reverse, db):
    id_token = json.dumps(
        {
            "id": 123,
            "email": "a@b.com",
            "email_verified": True,
        }
    )
    resp = client.post(
        headless_reverse("headless:socialaccount:provider_token"),
        data={
            "provider": "dummy",
            "token": {
                "id_token": id_token,
            },
            "process": AuthProcess.LOGIN,
        },
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.OK
    assert EmailAddress.objects.filter(email="a@b.com", verified=True).exists()


def test_invalid_token(client, headless_reverse, db, google_provider_settings):
    resp = client.post(
        headless_reverse("headless:socialaccount:provider_token"),
        data={
            "provider": "google",
            "token": {
                "id_token": "dummy",
                "client_id": google_provider_settings["APPS"][0]["client_id"],
            },
            "process": AuthProcess.LOGIN,
        },
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    data = resp.json()
    assert data == {
        "status": HTTPStatus.BAD_REQUEST,
        "errors": [
            {"message": "Invalid token.", "code": "invalid_token", "param": "token"}
        ],
    }


def test_valid_token_multiple_apps(
    client, headless_reverse, db, google_provider_settings, settings, user_factory
):
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    google_provider_settings["APPS"].append(
        {"client_id": "client_id2", "secret": "secret2"}
    )
    id_token = {"sub": "uid-from-id-token", "email": "a@b.com", "email_verified": True}
    with patch(
        "allauth.socialaccount.providers.google.views._verify_and_decode",
        return_value=id_token,
    ):
        resp = client.post(
            headless_reverse("headless:socialaccount:provider_token"),
            data={
                "provider": "google",
                "token": {
                    "id_token": "dummy",
                    "client_id": google_provider_settings["APPS"][0]["client_id"],
                },
                "process": AuthProcess.LOGIN,
            },
            content_type="application/json",
        )
        assert resp.status_code == HTTPStatus.OK


def test_auth_error_no_headless_request(client, db, google_provider_settings, settings):
    """Authentication errors use the regular "Third-Party Login Failure"
    template if headless is not used.
    """
    settings.HEADLESS_ONLY = False
    resp = client.get(reverse("google_callback"))
    assertTemplateUsed(resp, "socialaccount/authentication_error.html")


def test_auth_error_headless_request(
    client, db, google_provider_settings, sociallogin_setup_state
):
    """Authentication errors redirect to the next URL with ?error params for
    headless requests.
    """
    state = sociallogin_setup_state(client, headless=True, next="/foo")
    resp = client.get(reverse("google_callback") + f"?state={state}")
    assert resp["location"] == "/foo?error=unknown&error_process=login"


def test_auth_error_no_headless_state_request_headless_only(
    settings, client, db, google_provider_settings
):
    """Authentication errors redirect to a fallback error URL for headless-only,
    in case no next can be recovered from the state.
    """
    settings.HEADLESS_ONLY = True
    settings.HEADLESS_FRONTEND_URLS = {"socialaccount_login_error": "/3rdparty/failure"}
    resp = client.get(reverse("google_callback"))
    assert (
        resp["location"]
        == "http://testserver/3rdparty/failure?error=unknown&error_process=login"
    )


def test_auth_error_headless_state_request_headless_only(
    settings, client, db, google_provider_settings, sociallogin_setup_state
):
    """Authentication errors redirect to a fallback error URL for headless-only,
    in case no next can be recovered from the state.
    """
    state = sociallogin_setup_state(client, headless=True, next="/foo")
    settings.HEADLESS_ONLY = True
    settings.HEADLESS_FRONTEND_URLS = {"socialaccount_login_error": "/3rdparty/failure"}
    resp = client.get(reverse("google_callback") + f"?state={state}")
    assert resp["location"] == "/foo?error=unknown&error_process=login"


def test_token_signup_closed(client, headless_reverse, db):
    id_token = json.dumps(
        {
            "id": 123,
            "email": "a@b.com",
            "email_verified": True,
        }
    )
    with patch(
        "allauth.socialaccount.adapter.DefaultSocialAccountAdapter.is_open_for_signup"
    ) as iofs:
        iofs.return_value = False
        resp = client.post(
            headless_reverse("headless:socialaccount:provider_token"),
            data={
                "provider": "dummy",
                "token": {
                    "id_token": id_token,
                },
                "process": AuthProcess.LOGIN,
            },
            content_type="application/json",
        )
        assert resp.status_code == HTTPStatus.FORBIDDEN
    assert not EmailAddress.objects.filter(email="a@b.com", verified=True).exists()


def test_provider_signup(client, headless_reverse, db, settings):
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    settings.ACCOUNT_EMAIL_REQUIRED = True
    settings.ACCOUNT_USERNAME_REQUIRED = False
    account_uid = "123"
    id_token = json.dumps(
        {
            "id": account_uid,
        }
    )
    resp = client.post(
        headless_reverse("headless:socialaccount:provider_token"),
        data={
            "provider": "dummy",
            "token": {
                "id_token": id_token,
            },
            "process": AuthProcess.LOGIN,
        },
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    pending_flow = [f for f in resp.json()["data"]["flows"] if f.get("is_pending")][0]
    assert pending_flow["id"] == "provider_signup"

    resp = client.get(headless_reverse("headless:socialaccount:provider_signup"))
    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {
        "data": {
            "email": [],
            "account": {
                "display": "Dummy",
                "provider": {
                    "flows": ["provider_redirect", "provider_token"],
                    "id": "dummy",
                    "name": "Dummy",
                },
                "uid": account_uid,
            },
            "user": {"display": "user", "has_usable_password": False},
        },
        "status": HTTPStatus.OK,
    }

    resp = client.post(
        headless_reverse("headless:socialaccount:provider_signup"),
        data={
            "email": "a@b.com",
        },
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    pending_flow = [f for f in resp.json()["data"]["flows"] if f.get("is_pending")][0]
    assert pending_flow["id"] == "verify_email"
    assert EmailAddress.objects.filter(email="a@b.com").exists()


def test_signup_closed(client, headless_reverse, db, settings):
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    settings.ACCOUNT_EMAIL_REQUIRED = True
    settings.ACCOUNT_USERNAME_REQUIRED = False
    id_token = json.dumps(
        {
            "id": 123,
        }
    )
    resp = client.post(
        headless_reverse("headless:socialaccount:provider_token"),
        data={
            "provider": "dummy",
            "token": {
                "id_token": id_token,
            },
            "process": AuthProcess.LOGIN,
        },
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    pending_flow = [f for f in resp.json()["data"]["flows"] if f.get("is_pending")][0]
    assert pending_flow["id"] == "provider_signup"
    with patch(
        "allauth.socialaccount.adapter.DefaultSocialAccountAdapter.is_open_for_signup"
    ) as iofs:
        iofs.return_value = False
        resp = client.post(
            headless_reverse("headless:socialaccount:provider_signup"),
            data={
                "email": "a@b.com",
            },
            content_type="application/json",
        )
    assert resp.status_code == HTTPStatus.FORBIDDEN


def test_connect(user, auth_client, sociallogin_setup_state, headless_reverse, db):
    state = sociallogin_setup_state(
        auth_client, process="connect", next="/foo", headless=True
    )
    resp = auth_client.post(
        reverse("dummy_authenticate") + f"?state={state}",
        data={
            "id": 123,
        },
    )
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == "/foo"
    assert SocialAccount.objects.filter(user=user, provider="dummy", uid="123").exists()


def test_connect_reauthentication_required(
    user, auth_client, sociallogin_setup_state, headless_reverse, db, settings
):
    settings.ACCOUNT_REAUTHENTICATION_REQUIRED = True

    state = sociallogin_setup_state(
        auth_client, process="connect", next="/foo", headless=True
    )
    resp = auth_client.post(
        reverse("dummy_authenticate") + f"?state={state}",
        data={
            "id": 123,
        },
    )
    assert resp.status_code == HTTPStatus.FOUND
    assert (
        resp["location"] == "/foo?error=reauthentication_required&error_process=connect"
    )


def test_connect_already_connected(
    user, user_factory, auth_client, sociallogin_setup_state, headless_reverse, db
):
    # The other user already connected the account.
    other_user = user_factory()
    SocialAccount.objects.create(user=other_user, uid="123", provider="dummy")
    # Then, this user tries to connect...
    state = sociallogin_setup_state(
        auth_client, process=AuthProcess.CONNECT, next="/foo", headless=True
    )
    resp = auth_client.post(
        reverse("dummy_authenticate") + f"?state={state}",
        data={
            "id": 123,
        },
    )
    # We're redirected, and an error code is shown.
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == "/foo?error=connected_other&error_process=connect"
    assert not SocialAccount.objects.filter(
        user=user, provider="dummy", uid="123"
    ).exists()


def test_token_connect(user, auth_client, headless_reverse, db):
    id_token = json.dumps(
        {
            "id": 123,
            "email": "a@b.com",
            "email_verified": True,
        }
    )
    resp = auth_client.post(
        headless_reverse("headless:socialaccount:provider_token"),
        data={
            "provider": "dummy",
            "token": {
                "id_token": id_token,
            },
            "process": AuthProcess.CONNECT,
        },
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.OK
    assert SocialAccount.objects.filter(uid="123", user=user).exists()


def test_token_connect_already_connected(
    user, auth_client, headless_reverse, db, user_factory
):
    # The other user already connected the account.
    other_user = user_factory()
    SocialAccount.objects.create(user=other_user, uid="123", provider="dummy")
    id_token = json.dumps(
        {
            "id": 123,
            "email": "a@b.com",
            "email_verified": True,
        }
    )
    resp = auth_client.post(
        headless_reverse("headless:socialaccount:provider_token"),
        data={
            "provider": "dummy",
            "token": {
                "id_token": id_token,
            },
            "process": AuthProcess.CONNECT,
        },
        content_type="application/json",
    )
    assert not SocialAccount.objects.filter(uid="123", user=user).exists()
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json() == {
        "status": HTTPStatus.BAD_REQUEST,
        "errors": [
            {
                "code": "connected_other",
                "message": "The third-party account is already connected to a different account.",
            }
        ],
    }


def test_provider_signup_not_pending(client, headless_reverse, db, settings):
    resp = client.post(
        headless_reverse("headless:socialaccount:provider_signup"),
        data={
            "email": "a@b.com",
        },
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.CONFLICT


def test_valid_openid_connect_token(
    client, headless_reverse, db, openid_connect_provider_id
):
    provider = get_adapter().get_provider(None, openid_connect_provider_id)
    id_token = json.dumps(
        {
            "id": 123,
            "email": "a@b.com",
            "email_verified": True,
        }
    )
    with patch(
        "allauth.socialaccount.providers.openid_connect.views.OpenIDConnectOAuth2Adapter.openid_config"
    ):
        with patch("allauth.socialaccount.internal.jwtkit.verify_and_decode") as vad:
            vad.return_value = {"sub": "123"}
            resp = client.post(
                headless_reverse("headless:socialaccount:provider_token"),
                data={
                    "provider": openid_connect_provider_id,
                    "token": {
                        "client_id": provider.app.client_id,
                        "id_token": id_token,
                    },
                    "process": AuthProcess.LOGIN,
                },
                content_type="application/json",
            )
            assert resp.status_code == HTTPStatus.OK
            assert SocialAccount.objects.filter(uid="123").exists()
