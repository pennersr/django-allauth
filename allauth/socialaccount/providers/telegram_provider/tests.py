import base64
import json

from django.urls import reverse

import pytest
from pytest_django.asserts import assertTemplateUsed

from allauth.socialaccount.models import SocialAccount


@pytest.fixture
def telegram_app(settings):
    settings.SOCIALACCOUNT_PROVIDERS = {
        "telegram": {
            "APPS": [
                {
                    "client_id": "123",
                }
            ]
        }
    }


def test_login(client, db, telegram_app):
    resp = client.post(reverse("telegram_login"))
    assert resp.status_code == 302
    assert resp["location"].startswith(
        "https://oauth.telegram.org/auth?origin=http%3A%2F%2Ftestserver%2F&bot_id=123&request_access=write&embed=0&return_to=http%3A%2F%2Ftestserver%2Ftelegram%2Flogin%2Fcallback%2F%3Fstate%3D"
    )


def test_callback_get(client, db, telegram_app):
    resp = client.get(reverse("telegram_callback"))
    assert resp.status_code == 200
    assertTemplateUsed(resp, "telegram/callback.html")


def test_callback(client, db, telegram_app, sociallogin_setup_state):
    state = sociallogin_setup_state(client)
    auth_result = (
        base64.b64encode(
            json.dumps(
                {
                    "id": "123",
                    "hash": "0744ab643757850e82fa8b4ac35978dca287c81df6a9829032d868c7f90e3b99",
                    "auth_date": 2342342342,
                }
            ).encode("utf8")
        )
        .decode("ascii")
        .replace("=", "")
    )
    post_data = {
        "tgAuthResult": auth_result,
    }
    resp = client.post(reverse("telegram_callback") + f"?state={state}", post_data)
    assert resp.status_code == 302
    assert SocialAccount.objects.filter(uid="123").exists()
