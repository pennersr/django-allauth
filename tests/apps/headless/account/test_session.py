from http import HTTPStatus

from django.test.client import Client
from django.urls import reverse


def test_app_session_gone(db, user):
    # intentionally use a vanilla Django test client
    client = Client()
    # Force login, creates a Django session
    client.force_login(user)
    # That Django session should not play any role.
    resp = client.get(
        reverse("headless:app:account:current_session"), HTTP_X_SESSION_TOKEN="gone"
    )
    assert resp.status_code == HTTPStatus.GONE


def test_logout(auth_client, headless_reverse):
    # That Django session should not play any role.
    resp = auth_client.get(headless_reverse("headless:account:current_session"))
    assert resp.status_code == HTTPStatus.OK
    resp = auth_client.delete(headless_reverse("headless:account:current_session"))
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    resp = auth_client.get(headless_reverse("headless:account:current_session"))
    assert resp.status_code in [HTTPStatus.UNAUTHORIZED, HTTPStatus.GONE]


def test_logout_no_token(app_client, user):
    app_client.force_login(user)
    resp = app_client.get(reverse("headless:app:account:current_session"))
    assert resp.status_code == HTTPStatus.OK
    resp = app_client.delete(reverse("headless:app:account:current_session"))
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    assert "session_token" not in resp.json()["meta"]
