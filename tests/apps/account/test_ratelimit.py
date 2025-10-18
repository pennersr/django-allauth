from http import HTTPStatus

from django.urls import reverse


def test_case_insensitive_password_reset(settings, enable_cache, user_factory, client):
    settings.ACCOUNT_RATE_LIMITS = {"reset_password": "1/m"}
    user_factory(email="a@b.com")
    resp = client.post(reverse("account_reset_password"), data={"email": "a@b.com"})
    assert resp.status_code == HTTPStatus.FOUND
    resp = client.post(reverse("account_reset_password"), data={"email": "A@B.COM"})
    assert resp.status_code == HTTPStatus.TOO_MANY_REQUESTS
