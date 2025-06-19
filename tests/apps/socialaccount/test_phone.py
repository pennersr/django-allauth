from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse, reverse_lazy

import pytest

from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.socialaccount.models import SocialAccount


@pytest.mark.parametrize(
    "phone_verified, phone_valid, phone_taken, expected_url",
    [
        (True, True, False, settings.LOGIN_REDIRECT_URL),
        (False, True, False, reverse_lazy("account_verify_phone")),
        (True, False, False, reverse_lazy("socialaccount_signup")),
        (True, True, True, reverse_lazy("socialaccount_signup")),
    ],
)
def test_signup_with_phone(
    db,
    settings_impacting_urls,
    client,
    phone,
    phone_verified,
    phone_valid,
    phone_taken,
    expected_url,
    user_factory,
):
    if phone_taken:
        user_factory(phone=phone)
    with settings_impacting_urls(
        SOCIALACCOUNT_AUTO_SIGNUP=True,
        ACCOUNT_LOGIN_METHODS=("phone",),
        ACCOUNT_SIGNUP_FIELDS=["phone*"],
    ):
        resp = client.post(reverse("dummy_login"))
        assert resp.status_code == HTTPStatus.FOUND
        assert resp["location"].startswith(reverse("dummy_authenticate") + "?state=")
        resp = client.post(
            resp["location"],
            {
                "id": "123",
                "email": "a@b.com",
                "email_verified": True,
                "phone": phone if phone_valid else "*INVALID*",
                "phone_verified": phone_verified,
            },
        )
        assert resp.status_code == HTTPStatus.FOUND
        assert resp["location"] == expected_url
        if not phone_valid or phone_taken:
            return
        get_user_model().objects.filter(email="a@b.com").exists()
        socialaccount = SocialAccount.objects.get(uid="123")
        account = socialaccount.get_provider_account()
        assert account.to_str() == "a@b.com"
        assert get_account_adapter().get_phone(socialaccount.user) == (
            phone,
            phone_verified,
        )
