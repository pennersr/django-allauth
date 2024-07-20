from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse

from allauth.socialaccount.models import SocialAccount


def test_login(client, db):
    resp = client.post(reverse("dummy_login"))
    assert resp.status_code == 302
    assert resp["location"].startswith(reverse("dummy_authenticate") + "?state=")
    resp = client.post(
        resp["location"],
        {"id": "123", "email": "a@b.com", "email_verified": True},
    )
    assert resp.status_code == 302
    assert resp["location"] == settings.LOGIN_REDIRECT_URL
    get_user_model().objects.filter(email="a@b.com").exists()
    socialaccount = SocialAccount.objects.get(uid="123")
    account = socialaccount.get_provider_account()
    assert account.to_str() == "a@b.com"
