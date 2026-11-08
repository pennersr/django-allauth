import base64
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from http import HTTPStatus
from threading import Barrier, Lock
from unittest.mock import ANY
from urllib.parse import parse_qs, urlparse

from django.db import connection
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode

import jwt
import pytest
from oauthlib.common import Request
from pytest_django.asserts import assertTemplateUsed

from allauth.account.models import EmailAddress
from allauth.core.context import request_context
from allauth.idp.oidc.internal.oauthlib import authorization_codes
from allauth.idp.oidc.models import Token
from allauth.socialaccount.providers.oauth2.utils import generate_code_challenge


def test_cancel_authorization(auth_client, oidc_client):
    redirect_uri = oidc_client.get_redirect_uris()[0]
    resp = auth_client.get(
        reverse("idp:oidc:authorization")
        + "?"
        + urlencode(
            {
                "client_id": oidc_client.id,
                "response_type": "code",
                "redirect_uri": redirect_uri,
            }
        )
    )
    assert resp.status_code == HTTPStatus.OK
    assertTemplateUsed(resp, "idp/oidc/authorization_form.html")
    resp = auth_client.post(
        reverse("idp:oidc:authorization"),
        {
            "request": resp.context["form"]["request"].value(),
        },
    )
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == f"{redirect_uri}?error=access_denied"


@pytest.mark.parametrize(
    "access_token_format,scopes,has_secondary_email,choose_secondary_email,resources",
    [
        ("opaque", ("openid", "profile", "email"), False, False, []),
        (
            "opaque",
            ("openid", "profile", "email"),
            False,
            False,
            ["https://api.example.com/a"],
        ),
        (
            "opaque",
            ("openid", "profile", "email"),
            False,
            False,
            ["https://api.example.com/a", "https://api.example.com/b"],
        ),
        ("opaque", ("openid", "profile", "email"), True, False, []),
        ("opaque", ("openid", "profile", "email"), True, True, []),
        ("opaque", ("openid", "profile"), False, False, []),
        ("opaque", ("openid",), False, False, []),
        ("jwt", ("openid",), False, False, []),
        (
            "jwt",
            ("openid",),
            False,
            False,
            ["https://api.example.com/a"],
        ),
        (
            "jwt",
            ("openid",),
            False,
            False,
            ["https://api.example.com/a", "https://api.example.com/b"],
        ),
    ],
)
def test_authorization_code_flow(
    auth_client,
    user,
    oidc_client,
    oidc_client_secret,
    scopes,
    has_secondary_email,
    choose_secondary_email,
    email_factory,
    settings,
    access_token_format,
    resources,
):
    settings.IDP_OIDC_ACCESS_TOKEN_FORMAT = access_token_format
    secondary_email = email_factory()
    EmailAddress.objects.create(
        user=user,
        email=secondary_email,
        primary=False,
        verified=True,
    )
    redirect_uri = oidc_client.get_redirect_uris()[0]
    resp = auth_client.get(
        reverse("idp:oidc:authorization")
        + "?"
        + urlencode(
            {
                "client_id": oidc_client.id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": " ".join(scopes),
                "nonce": "some-nonce",
                "state": "some-state",
                "resource": resources,
            },
            doseq=True,
        )
    )
    assert resp.status_code == HTTPStatus.OK
    assertTemplateUsed(resp, "idp/oidc/authorization_form.html")
    post_data = {
        "scopes": scopes,
        "action": "grant",
        "request": resp.context["form"]["request"].value(),
    }
    expected_email = secondary_email if choose_secondary_email else user.email
    if has_secondary_email and "email" in scopes:
        post_data["email"] = expected_email
    resp = auth_client.post(
        reverse("idp:oidc:authorization"),
        post_data,
    )
    assert resp.status_code == HTTPStatus.FOUND
    redirected_uri = resp["location"]
    assert redirected_uri.startswith(redirect_uri)
    parts = urlparse(redirected_uri)
    params = parse_qs(parts.query)
    code = params["code"][0]
    assert params["state"][0] == "some-state"
    resp = auth_client.post(
        reverse("idp:oidc:token"),
        {
            "code": code,
            "grant_type": "authorization_code",
            "client_id": oidc_client.id,
            "client_secret": oidc_client_secret,
            "redirect_uri": redirect_uri,
        },
    )
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert set(data.keys()) == {
        "access_token",
        "expires_in",
        "token_type",
        "scope",
        "refresh_token",
        "id_token",
    }

    access_token = Token.objects.lookup(Token.Type.ACCESS_TOKEN, data["access_token"])
    refresh_token = Token.objects.lookup(
        Token.Type.REFRESH_TOKEN, data["refresh_token"]
    )
    assert access_token.get_grant_id() == refresh_token.get_grant_id()
    assert set(access_token.get_resources()) == set(resources)
    assert bool(access_token.get_scope_email()) == bool(
        "email" in scopes and has_secondary_email and choose_secondary_email
    )

    # Access token
    if access_token_format == "jwt":
        decoded = jwt.decode(data["access_token"], options={"verify_signature": False})
        expected_decoded = {
            "client_id": oidc_client.id,
            "exp": ANY,
            "iat": ANY,
            "iss": "http://testserver",
            "jti": ANY,
            "scope": " ".join(scopes),
            "sub": str(user.pk),
            "token_use": "access",
        }
        if resources:
            expected_decoded["aud"] = resources
        assert decoded == expected_decoded

    # ID token
    id_token = data["id_token"]
    decoded = jwt.decode(id_token, options={"verify_signature": False})
    assert decoded["sub"] == str(user.pk)
    assert decoded["nonce"] == "some-nonce"
    if "email" in scopes:
        assert decoded["email"] == expected_email
    else:
        assert "email" not in decoded
    if "profile" in scopes:
        assert decoded["preferred_username"] == user.username
    else:
        assert "preferred_username" not in decoded


@pytest.mark.django_db(transaction=True)
def test_authorization_code_concurrent_redemption(
    user,
    oidc_client,
    oidc_client_secret,
    monkeypatch,
    authorization_code_factory,
):
    if connection.vendor == "sqlite":
        pytest.skip("SQLite serializes concurrent writes")
    code = uuid.uuid4().hex
    pkce = generate_code_challenge()
    authorization_code_factory(oidc_client=oidc_client, user=user, code=code, pkce=pkce)

    workers = 8
    lookup_barrier = Barrier(workers)
    original_lookup = authorization_codes.lookup

    def synchronized_lookup(client_id, candidate):
        code_token = original_lookup(client_id, candidate)
        if candidate == code:
            lookup_barrier.wait()
        return code_token

    monkeypatch.setattr(authorization_codes, "lookup", synchronized_lookup)
    # SQLite cannot perform the revocation deletes concurrently. Record the
    # post-commit calls and execute the real query after all workers finish.
    original_revoke_tokens = authorization_codes._revoke_tokens
    revocations = []
    revocations_lock = Lock()

    def record_revocation(client_id, user_id, grant_id):
        with revocations_lock:
            revocations.append((client_id, user_id, grant_id))

    monkeypatch.setattr(authorization_codes, "_revoke_tokens", record_revocation)
    redirect_uri = oidc_client.get_redirect_uris()[0]

    def redeem(_):
        client = Client()
        return client.post(
            reverse("idp:oidc:token"),
            {
                "code": code,
                "code_verifier": pkce["code_verifier"],
                "grant_type": "authorization_code",
                "client_id": oidc_client.id,
                "client_secret": oidc_client_secret,
                "redirect_uri": redirect_uri,
            },
        )

    with ThreadPoolExecutor(max_workers=workers) as executor:
        responses = list(executor.map(redeem, range(workers)))

    assert [response.status_code for response in responses].count(HTTPStatus.OK) == 1
    errors = [
        response.json()
        for response in responses
        if response.status_code == HTTPStatus.BAD_REQUEST
    ]
    assert errors == [{"error": "invalid_grant"}] * (workers - 1)
    issued_tokens = next(
        response.json()
        for response in responses
        if response.status_code == HTTPStatus.OK
    )
    issued_access_token = Token.objects.lookup(
        Token.Type.ACCESS_TOKEN, issued_tokens["access_token"]
    )
    issued_refresh_token = Token.objects.lookup(
        Token.Type.REFRESH_TOKEN, issued_tokens["refresh_token"]
    )
    assert issued_access_token
    assert issued_refresh_token
    grant_id = issued_access_token.get_grant_id()
    assert grant_id
    assert revocations
    assert {
        (client_id, user_id, grant_id) for client_id, user_id, grant_id in revocations
    } == {(oidc_client.id, user.pk, grant_id)}
    original_revoke_tokens(*revocations[0])
    assert not Token.objects.lookup(
        Token.Type.ACCESS_TOKEN, issued_tokens["access_token"]
    )
    assert not Token.objects.lookup(
        Token.Type.REFRESH_TOKEN, issued_tokens["refresh_token"]
    )


def test_invalid_authorization_code_is_not_claimed(
    oidc_client,
    oidc_client_secret,
    client,
):
    code = uuid.uuid4().hex
    response = client.post(
        reverse("idp:oidc:token"),
        {
            "code": code,
            "grant_type": "authorization_code",
            "client_id": oidc_client.id,
            "client_secret": oidc_client_secret,
            "redirect_uri": oidc_client.get_redirect_uris()[0],
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {"error": "invalid_grant"}
    assert (
        not Token.objects.by_value(code)
        .filter(client=oidc_client, type=Token.Type.AUTHORIZATION_CODE)
        .exists()
    )


def test_claim_requires_validation(rf):
    with request_context(rf.get("/")):
        with pytest.raises(RuntimeError, match="was not validated"):
            authorization_codes.claim("client", "code", Request("/"))


@pytest.mark.parametrize("invalid_parameter", ["code_verifier", "redirect_uri"])
def test_authorization_code_claimed_after_validation(
    user,
    oidc_client,
    oidc_client_secret,
    client,
    authorization_code_factory,
    invalid_parameter,
):
    code = uuid.uuid4().hex
    pkce = generate_code_challenge()
    authorization_code_factory(oidc_client=oidc_client, user=user, code=code, pkce=pkce)
    token_data = {
        "code": code,
        "code_verifier": pkce["code_verifier"],
        "grant_type": "authorization_code",
        "client_id": oidc_client.id,
        "client_secret": oidc_client_secret,
        "redirect_uri": oidc_client.get_redirect_uris()[0],
    }
    invalid_token_data = dict(token_data)
    if invalid_parameter == "code_verifier":
        invalid_token_data[invalid_parameter] = generate_code_challenge()[
            "code_verifier"
        ]
    else:
        invalid_token_data[invalid_parameter] = "https://attacker.example/callback"

    response = client.post(reverse("idp:oidc:token"), invalid_token_data)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    code_token = Token.objects.by_value(code).get(
        client=oidc_client, type=Token.Type.AUTHORIZATION_CODE
    )
    assert code_token.data["claimed"] is False

    response = client.post(reverse("idp:oidc:token"), token_data)

    assert response.status_code == HTTPStatus.OK


def test_authorization_code_reuse_revokes_tokens(
    user,
    user_factory,
    oidc_client,
    oidc_client_secret,
    client,
    django_capture_on_commit_callbacks,
    authorization_code_factory,
):
    code = uuid.uuid4().hex
    authorization_code_factory(oidc_client=oidc_client, user=user, code=code)
    token_data = {
        "code": code,
        "grant_type": "authorization_code",
        "client_id": oidc_client.id,
        "client_secret": oidc_client_secret,
        "redirect_uri": oidc_client.get_redirect_uris()[0],
    }

    response = client.post(reverse("idp:oidc:token"), token_data)
    assert response.status_code == HTTPStatus.OK
    issued_tokens = response.json()
    access_token = Token.objects.lookup(
        Token.Type.ACCESS_TOKEN, issued_tokens["access_token"]
    )
    assert access_token
    assert Token.objects.lookup(
        Token.Type.REFRESH_TOKEN, issued_tokens["refresh_token"]
    )
    grant_id = access_token.get_grant_id()
    assert grant_id
    unrelated_token = Token.objects.create(
        client=oidc_client,
        user=user_factory(),
        type=Token.Type.ACCESS_TOKEN,
        hash=uuid.uuid4().hex,
    )
    unrelated_token.set_grant_id(grant_id)
    unrelated_token.save(update_fields=["data"])
    with django_capture_on_commit_callbacks(execute=True):
        response = client.post(reverse("idp:oidc:token"), token_data)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {"error": "invalid_grant"}
    assert not Token.objects.lookup(
        Token.Type.ACCESS_TOKEN, issued_tokens["access_token"]
    )
    assert not Token.objects.lookup(
        Token.Type.REFRESH_TOKEN, issued_tokens["refresh_token"]
    )
    assert Token.objects.filter(pk=unrelated_token.pk).exists()


def test_hybrid_flow_uses_one_grant_id(
    auth_client,
    oidc_client,
    oidc_client_secret,
):
    oidc_client.set_response_types(["code token"])
    oidc_client.skip_consent = True
    oidc_client.save()
    redirect_uri = oidc_client.get_redirect_uris()[0]
    resp = auth_client.get(
        reverse("idp:oidc:authorization")
        + "?"
        + urlencode(
            {
                "client_id": oidc_client.id,
                "redirect_uri": redirect_uri,
                "response_type": "code token",
                "scope": "openid",
                "nonce": "some-nonce",
            }
        )
    )
    assert resp.status_code == HTTPStatus.FOUND
    authorization_data = parse_qs(urlparse(resp["location"]).fragment)
    hybrid_access_token = Token.objects.lookup(
        Token.Type.ACCESS_TOKEN, authorization_data["access_token"][0]
    )

    resp = auth_client.post(
        reverse("idp:oidc:token"),
        {
            "code": authorization_data["code"][0],
            "grant_type": "authorization_code",
            "client_id": oidc_client.id,
            "client_secret": oidc_client_secret,
            "redirect_uri": redirect_uri,
        },
    )

    assert resp.status_code == HTTPStatus.OK
    token_data = resp.json()
    access_token = Token.objects.lookup(
        Token.Type.ACCESS_TOKEN, token_data["access_token"]
    )
    refresh_token = Token.objects.lookup(
        Token.Type.REFRESH_TOKEN, token_data["refresh_token"]
    )
    grant_ids = {
        hybrid_access_token.get_grant_id(),
        access_token.get_grant_id(),
        refresh_token.get_grant_id(),
    }
    assert None not in grant_ids
    assert len(grant_ids) == 1


@pytest.mark.parametrize(
    "token_endpoint_auth_method", ["client_secret_post", "client_secret_basic"]
)
def test_authorization_code_flow_skip_consent(
    auth_client,
    user,
    oidc_client,
    oidc_client_secret,
    token_endpoint_auth_method,
):
    oidc_client.skip_consent = True
    oidc_client.save()
    redirect_uri = oidc_client.get_redirect_uris()[0]
    resp = auth_client.get(
        reverse("idp:oidc:authorization")
        + "?"
        + urlencode(
            {
                "client_id": oidc_client.id,
                "response_type": "code",
                "scope": "openid profile email",
                "nonce": "some-nonce",
                "state": "some-state",
                "redirect_uri": redirect_uri,
            }
        )
    )
    assert resp.status_code == HTTPStatus.FOUND
    redirected_uri = resp["location"]
    assert redirected_uri.startswith(redirect_uri)
    parts = urlparse(redirected_uri)
    params = parse_qs(parts.query)
    code = params["code"][0]
    token_data = {
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }
    token_kwargs = {}
    if token_endpoint_auth_method == "client_secret_basic":
        credentials = base64.b64encode(
            f"{oidc_client.id}:{oidc_client_secret}".encode()
        ).decode()
        token_kwargs["HTTP_AUTHORIZATION"] = f"Basic {credentials}"
    else:
        token_data.update(
            {
                "client_id": oidc_client.id,
                "client_secret": oidc_client_secret,
            }
        )
    resp = auth_client.post(reverse("idp:oidc:token"), token_data, **token_kwargs)
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert set(data.keys()) == {
        "access_token",
        "expires_in",
        "token_type",
        "scope",
        "refresh_token",
        "id_token",
    }


@pytest.mark.parametrize("refresh_token_expires_in", [None, 3600])
def test_authorization_code_flow_refresh_token_expiry(
    auth_client,
    oidc_client,
    oidc_client_secret,
    settings,
    refresh_token_expires_in,
):
    # The initially issued refresh token carries the configured expiry, and
    # the lifetime is exposed in the token response as ``refresh_expires_in``.
    settings.IDP_OIDC_REFRESH_TOKEN_EXPIRES_IN = refresh_token_expires_in
    oidc_client.skip_consent = True
    oidc_client.save()
    redirect_uri = oidc_client.get_redirect_uris()[0]
    resp = auth_client.get(
        reverse("idp:oidc:authorization")
        + "?"
        + urlencode(
            {
                "client_id": oidc_client.id,
                "response_type": "code",
                "scope": "openid",
                "nonce": "some-nonce",
                "state": "some-state",
                "redirect_uri": redirect_uri,
            }
        )
    )
    assert resp.status_code == HTTPStatus.FOUND
    code = parse_qs(urlparse(resp["location"]).query)["code"][0]
    resp = auth_client.post(
        reverse("idp:oidc:token"),
        {
            "code": code,
            "grant_type": "authorization_code",
            "client_id": oidc_client.id,
            "client_secret": oidc_client_secret,
            "redirect_uri": redirect_uri,
        },
    )
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    refresh_token = Token.objects.lookup(
        Token.Type.REFRESH_TOKEN, data["refresh_token"]
    )
    if refresh_token_expires_in:
        assert abs(data["refresh_expires_in"] - refresh_token_expires_in) < 30
        expected = timezone.now() + timedelta(seconds=refresh_token_expires_in)
        assert abs((refresh_token.expires_at - expected).total_seconds()) < 30
    else:
        assert "refresh_expires_in" not in data
        assert refresh_token.expires_at is None


def test_authorization_id_token_hint_match(
    user, id_token_factory, oidc_client, auth_client, user_factory
):
    redirect_uri = oidc_client.get_redirect_uris()[0]
    # Pass along ID token as hint
    resp = auth_client.get(
        reverse("idp:oidc:authorization")
        + "?"
        + urlencode(
            {
                "client_id": oidc_client.id,
                "id_token_hint": id_token_factory(oidc_client, user),
                "response_type": "code",
                "scope": "openid",
                "nonce": "some-nonce",
                "state": "some-state",
                "redirect_uri": redirect_uri,
            }
        )
    )
    assert resp.status_code == HTTPStatus.OK


def test_authorization_id_token_hint_mismatch(
    user, id_token_factory, oidc_client, auth_client, user_factory
):
    redirect_uri = oidc_client.get_redirect_uris()[0]
    # Pass along ID token as hint
    resp = auth_client.get(
        reverse("idp:oidc:authorization")
        + "?"
        + urlencode(
            {
                "client_id": oidc_client.id,
                "id_token_hint": id_token_factory(oidc_client, user_factory()),
                "response_type": "code",
                "redirect_uri": redirect_uri,
                "scope": "openid",
                "nonce": "some-nonce",
                "state": "some-state",
            }
        )
    )
    assert resp.status_code == HTTPStatus.FOUND
    parts = urlparse(resp["location"])
    params = parse_qs(parts.query)
    assert params["error"] == ["login_required"]
    assert params["error_description"] == [
        "Session user does not match client supplied user."
    ]


def test_authorization_post_redirects_to_get(auth_client):
    payload = {
        "client_id": "c123",
        "response_type": "code",
        "scope": "openid",
        "nonce": "some-nonce",
        "state": "some-state",
    }
    resp = auth_client.post(reverse("idp:oidc:authorization"), data=payload)
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == reverse("idp:oidc:authorization") + "?" + urlencode(
        payload
    )


def test_authorization_post_redirects_anon_to_get(db, client):
    payload = {
        "client_id": "c123",
        "response_type": "code",
        "scope": "openid",
        "nonce": "some-nonce",
        "state": "some-state",
    }
    resp = client.post(reverse("idp:oidc:authorization"), data=payload, follow=True)
    assert resp.status_code == HTTPStatus.OK
    url = f"{reverse('idp:oidc:authorization')}?{urlencode(payload)}"
    assert resp.redirect_chain == [
        (url, HTTPStatus.FOUND),
        (
            reverse("account_login")
            + "?"
            + urlencode({"next": url}).replace("%2F", "/"),
            HTTPStatus.FOUND,
        ),
    ]


def test_authorization_post_is_csrf_protected(user):
    client = Client(enforce_csrf_checks=True)
    client.force_login(user)
    payload = {
        "request": "dummy",
        "scopes": "openid",
    }
    resp = client.post(reverse("idp:oidc:authorization"), data=payload)
    assert resp.status_code == HTTPStatus.FORBIDDEN
    assert b"CSRF Failed" in resp.content


@pytest.mark.parametrize("valid_code_verifier", [False, True])
def test_authorization_code_flow_with_pkce(
    auth_client,
    user,
    oidc_client,
    valid_code_verifier,
):
    oidc_client.type = oidc_client.Type.PUBLIC
    oidc_client.save()
    redirect_uri = oidc_client.get_redirect_uris()[0]
    scopes = ["openid", "profile", "email"]
    pkce = generate_code_challenge()
    resp = auth_client.get(
        reverse("idp:oidc:authorization")
        + "?"
        + urlencode(
            {
                "client_id": oidc_client.id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": " ".join(scopes),
                "nonce": "some-nonce",
                "state": "some-state",
                "code_challenge": pkce["code_challenge"],
                "code_challenge_method": pkce["code_challenge_method"],
            }
        )
    )
    assert resp.status_code == HTTPStatus.OK
    assertTemplateUsed(resp, "idp/oidc/authorization_form.html")
    resp = auth_client.post(
        reverse("idp:oidc:authorization"),
        {
            "scopes": scopes,
            "action": "grant",
            "request": resp.context["form"]["request"].value(),
        },
    )
    assert resp.status_code == HTTPStatus.FOUND
    redirected_uri = resp["location"]
    assert redirected_uri.startswith(redirect_uri)
    parts = urlparse(redirected_uri)
    params = parse_qs(parts.query)
    code = params["code"][0]
    assert params["state"][0] == "some-state"
    resp = auth_client.post(
        reverse("idp:oidc:token"),
        {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": oidc_client.id,
            "redirect_uri": redirect_uri,
            "state": "some-state",
            "code_verifier": pkce["code_verifier"] if valid_code_verifier else "WRONG",
        },
    )
    if not valid_code_verifier:
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        return

    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert set(data.keys()) == {
        "access_token",
        "expires_in",
        "id_token",
        "token_type",
        "scope",
        "refresh_token",
    }


@pytest.mark.parametrize("code_challenge_method", [None, "plain"])
@pytest.mark.parametrize("scope", ["openid", "profile"])
def test_authorization_code_flow_pkce_requires_s256(
    auth_client,
    oidc_client,
    code_challenge_method,
    scope,
):
    oidc_client.type = oidc_client.Type.PUBLIC
    oidc_client.save()
    redirect_uri = oidc_client.get_redirect_uris()[0]
    pkce = generate_code_challenge()
    params = {
        "client_id": oidc_client.id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": scope,
        "code_challenge": pkce["code_challenge"],
    }
    if code_challenge_method is not None:
        params["code_challenge_method"] = code_challenge_method

    resp = auth_client.get(reverse("idp:oidc:authorization") + "?" + urlencode(params))

    assert resp.status_code == HTTPStatus.FOUND
    error_params = parse_qs(urlparse(resp["location"]).query)
    assert error_params["error"] == ["invalid_request"]
    assert error_params["error_description"] == ["Transform algorithm not supported."]


@pytest.mark.parametrize("client_fixture", ["auth_client", "client"])
@pytest.mark.parametrize(
    "prompt,next_prompt", [("login", None), ("login consent", "consent")]
)
def test_redirect_to_login_with_prompt_login(
    request, client_fixture, oidc_client, prompt, next_prompt
):
    client = request.getfixturevalue(client_fixture)
    redirect_uri = oidc_client.get_redirect_uris()[0]
    resp = client.get(
        reverse("idp:oidc:authorization")
        + "?"
        + urlencode(
            {
                "client_id": oidc_client.id,
                "response_type": "code",
                "redirect_uri": redirect_uri,
                "prompt": prompt,
            }
        )
    )
    assert resp.status_code == HTTPStatus.FOUND
    parts = urlparse(resp["location"])
    assert parts.path == reverse(
        "account_login" if client_fixture == "client" else "account_reauthenticate"
    )
    params = parse_qs(parts.query)
    params = parse_qs(urlparse(params["next"][0]).query)
    if next_prompt:
        assert params["prompt"][0] == next_prompt
    else:
        assert "prompt" not in params


def test_prompt_login_with_code_only_reauthentication(
    auth_client, oidc_client, settings
):
    settings.ACCOUNT_REAUTHENTICATION_METHODS = {"code"}
    redirect_uri = oidc_client.get_redirect_uris()[0]

    resp = auth_client.get(
        reverse("idp:oidc:authorization")
        + "?"
        + urlencode(
            {
                "client_id": oidc_client.id,
                "response_type": "code",
                "redirect_uri": redirect_uri,
                "prompt": "login",
            }
        )
    )

    assert resp.status_code == HTTPStatus.FOUND
    assert urlparse(resp["location"]).path == reverse(
        "account_request_reauthentication_code"
    )


@pytest.mark.parametrize(
    "client_fixture,scope,error",
    [
        ("auth_client", "openid", None),
        ("auth_client", "openid profile", "consent_required"),
        ("client", "openid", "login_required"),
    ],
)
def test_prompt_none(
    request,
    client_fixture,
    scope,
    error,
    oidc_client,
    user,
    access_token_factory,
):
    access_token_factory(oidc_client, user, scopes=["openid"])
    client = request.getfixturevalue(client_fixture)
    redirect_uri = oidc_client.get_redirect_uris()[0]
    resp = client.get(
        reverse("idp:oidc:authorization")
        + "?"
        + urlencode(
            {
                "client_id": oidc_client.id,
                "response_type": "code",
                "scope": scope,
                "redirect_uri": redirect_uri,
                "prompt": "none",
            }
        )
    )
    assert resp.status_code == HTTPStatus.FOUND
    if error:
        assert resp["location"] == f"https://rp.client/callback?error={error}"
    else:
        assert resp["location"].startswith("https://rp.client/callback?code=")


def test_prompt_none_requires_consent_for_client(
    auth_client,
    oidc_client,
    oidc_client_factory,
    user,
    access_token_factory,
):
    other_client = oidc_client_factory()
    access_token_factory(other_client, user, scopes=["openid"])
    redirect_uri = oidc_client.get_redirect_uris()[0]

    resp = auth_client.get(
        reverse("idp:oidc:authorization")
        + "?"
        + urlencode(
            {
                "client_id": oidc_client.id,
                "response_type": "code",
                "scope": "openid",
                "redirect_uri": redirect_uri,
                "prompt": "none",
            }
        )
    )

    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == f"{redirect_uri}?error=consent_required"


def test_authorization_code_invalid_with_resource(
    auth_client,
    user,
    oidc_client,
    oidc_client_secret,
):
    redirect_uri = oidc_client.get_redirect_uris()[0]
    resp = auth_client.get(
        reverse("idp:oidc:authorization")
        + "?"
        + urlencode(
            {
                "client_id": oidc_client.id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": " ".join(["openid"]),
                "nonce": "some-nonce",
                "state": "some-state",
                "resource": ["https://api.example.com", "mailto:info@allauth.org"],
            },
            doseq=True,
        )
    )
    assert resp.status_code == HTTPStatus.OK
    assertTemplateUsed(resp, "idp/oidc/error.html")


@pytest.mark.parametrize(
    "granted_resources,requested_resources,success",
    [
        ([], ["https://api.example.com/a"], True),
        (["https://api.example.com"], ["https://api.example.com/a"], True),
        (["https://api.example.org"], ["https://api.example.com/a"], False),
        (
            ["https://api.example.org", "https://api.example.com"],
            ["https://api.example.com/a"],
            True,
        ),
        (["https://api.example.com/a"], ["https://api.example.com/b"], False),
    ],
)
def test_authorization_code_requested_granted_resources(
    auth_client,
    user,
    oidc_client,
    oidc_client_secret,
    granted_resources,
    requested_resources,
    success,
):
    redirect_uri = oidc_client.get_redirect_uris()[0]
    data = {
        "client_id": oidc_client.id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid",
        "nonce": "some-nonce",
        "state": "some-state",
    }
    if granted_resources:
        data["resource"] = granted_resources
    resp = auth_client.get(
        reverse("idp:oidc:authorization") + "?" + urlencode(data, doseq=True)
    )
    assert resp.status_code == HTTPStatus.OK
    assertTemplateUsed(resp, "idp/oidc/authorization_form.html")
    post_data = {
        "scopes": "openid",
        "action": "grant",
        "request": resp.context["form"]["request"].value(),
    }
    resp = auth_client.post(
        reverse("idp:oidc:authorization"),
        post_data,
    )
    assert resp.status_code == HTTPStatus.FOUND
    redirected_uri = resp["location"]
    assert redirected_uri.startswith(redirect_uri)
    parts = urlparse(redirected_uri)
    params = parse_qs(parts.query)
    code = params["code"][0]
    assert params["state"][0] == "some-state"
    data = {
        "code": code,
        "grant_type": "authorization_code",
        "client_id": oidc_client.id,
        "client_secret": oidc_client_secret,
        "redirect_uri": redirect_uri,
    }
    if requested_resources:
        data["resource"] = requested_resources
    resp = auth_client.post(reverse("idp:oidc:token"), data)
    if success:
        assert resp.status_code == HTTPStatus.OK
        data = resp.json()
        assert set(data.keys()) == {
            "access_token",
            "expires_in",
            "token_type",
            "scope",
            "refresh_token",
            "id_token",
        }

        access_token = Token.objects.lookup(
            Token.Type.ACCESS_TOKEN, data["access_token"]
        )
        assert set(access_token.get_resources()) == set(requested_resources)
    else:
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        data = resp.json()
        assert data == {
            "error": "invalid_target",
            "error_description": "The requested resource is invalid, missing, unknown, or malformed.",
        }


@pytest.mark.parametrize("skip_consent", [False, True])
@pytest.mark.parametrize("action", ["grant", "deny"])
def test_authorization_code_app_redirect_uri(
    auth_client,
    user,
    oidc_client,
    oidc_client_secret,
    skip_consent,
    action,
):
    redirect_uri = "org.allauth.app://callback"
    oidc_client.set_redirect_uris([redirect_uri])
    oidc_client.skip_consent = skip_consent
    oidc_client.save()
    resp = auth_client.get(
        reverse("idp:oidc:authorization")
        + "?"
        + urlencode(
            {
                "client_id": oidc_client.id,
                "response_type": "code",
                "scope": "openid profile email",
                "nonce": "some-nonce",
                "state": "some-state",
                "redirect_uri": redirect_uri,
            }
        )
    )
    if not skip_consent:
        assert resp.status_code == HTTPStatus.OK
        post_data = {
            "scopes": ["openid"],
            "action": action,
            "request": resp.context["form"]["request"].value(),
        }
        resp = auth_client.post(
            reverse("idp:oidc:authorization"),
            post_data,
        )
        if action == "deny":
            assert (
                resp["location"]
                == f"{redirect_uri}?error=access_denied&state=some-state"
            )
            return

    assert resp.status_code == HTTPStatus.FOUND
    redirected_uri = resp["location"]
    assert redirected_uri.startswith(redirect_uri)


@pytest.mark.parametrize(
    "client_fixture,scope,error",
    [
        ("client", "openid", "login_required"),
        ("auth_client", "openid profile", "consent_required"),
    ],
)
def test_prompt_none_app_redirect_uri(
    request,
    client_fixture,
    scope,
    error,
    oidc_client,
    user,
    access_token_factory,
):
    """Errors are redirected to app native redirect URIs as well."""
    redirect_uri = "org.allauth.app://callback"
    oidc_client.set_redirect_uris([redirect_uri])
    oidc_client.save()
    access_token_factory(oidc_client, user, scopes=["openid"])
    client = request.getfixturevalue(client_fixture)
    resp = client.get(
        reverse("idp:oidc:authorization")
        + "?"
        + urlencode(
            {
                "client_id": oidc_client.id,
                "response_type": "code",
                "scope": scope,
                "redirect_uri": redirect_uri,
                "state": "some-state",
                "prompt": "none",
            }
        )
    )
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == f"{redirect_uri}?error={error}&state=some-state"
