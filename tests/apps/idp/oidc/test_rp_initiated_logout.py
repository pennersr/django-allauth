from http import HTTPStatus

from django.urls import reverse
from django.utils.http import urlencode

import pytest

from allauth.idp.oidc.models import Token


@pytest.mark.parametrize("method", ["GET", "POST"])
@pytest.mark.parametrize(
    "post_logout_redirect_uri,state,expected_location",
    [
        (None, None, "/"),
        ("https://rp.client/logged-out", None, "https://rp.client/logged-out"),
        (
            "https://rp.client/logged-out",
            "mystate",
            "https://rp.client/logged-out?state=mystate",
        ),
        ("http://no-http.org/please", None, "/"),
    ],
)
def test_logout_while_anonymous(
    method, client, post_logout_redirect_uri, state, expected_location
):
    params = {}
    if post_logout_redirect_uri:
        params["post_logout_redirect_uri"] = post_logout_redirect_uri
    if state:
        params["state"] = state
    if method == "GET":
        query = None
        if params:
            query = urlencode(params)
        resp = client.get(reverse("idp:oidc:logout") + (f"?{query}" if query else ""))
    else:
        resp = client.post(reverse("idp:oidc:logout"), data=params)
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == expected_location


@pytest.mark.parametrize("method", ["GET", "POST"])
def test_logout_must_ask(auth_client, settings, method):
    settings.IDP_OIDC_RP_INITIATED_LOGOUT_ASKS_FOR_OP_LOGOUT = False
    params = {}
    if method == "GET":
        query = None
        if params:
            query = urlencode(params)
        resp = auth_client.get(
            reverse("idp:oidc:logout") + (f"?{query}" if query else "")
        )
    else:
        resp = auth_client.post(reverse("idp:oidc:logout"), data=params)
    assert resp.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    "csrfmiddlewaretoken, status_code",
    [(None, HTTPStatus.OK), ("", HTTPStatus.FORBIDDEN), ("hack", HTTPStatus.FORBIDDEN)],
)
def test_rp_cannot_bypass(auth_client, csrfmiddlewaretoken, status_code):
    auth_client.enforce_csrf_checks = True
    auth_client.handler.enforce_csrf_checks = True
    params = {
        # Try a POST that answers the question right away...
        "action": "logout",
    }
    if csrfmiddlewaretoken is not None:
        params["csrfmiddlewaretoken"] = "hack"
    resp = auth_client.post(reverse("idp:oidc:logout"), data=params)
    assert resp.status_code == status_code


@pytest.mark.parametrize("method", ["GET", "POST"])
def test_logout_without_asking(
    auth_client,
    user,
    settings,
    method,
    oidc_client,
    id_token_generator,
    access_token_generator,
    refresh_token_factory,
):
    id_token_hint = id_token_generator(oidc_client, user)
    access_token, access_token_instance = access_token_generator(oidc_client, user)
    refresh_token, refresh_token_instance = refresh_token_factory(
        user=user, client=oidc_client
    )
    settings.IDP_OIDC_RP_INITIATED_LOGOUT_ASKS_FOR_OP_LOGOUT = False
    params = {
        "id_token_hint": id_token_hint,
        "post_logout_redirect_uri": "https://rp.client/logged-out",
    }
    if method == "GET":
        query = None
        if params:
            query = urlencode(params)
        resp = auth_client.get(
            reverse("idp:oidc:logout") + (f"?{query}" if query else "")
        )
    else:
        resp = auth_client.post(reverse("idp:oidc:logout"), data=params)
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == "https://rp.client/logged-out"

    assert not Token.objects.filter(pk=access_token_instance.pk).exists()
    assert not Token.objects.filter(pk=refresh_token_instance.pk).exists()
    resp = auth_client.get(reverse("account_email"))
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"].startswith(reverse("account_login"))
