from django.test import TestCase

import pytest

from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.openid_connect.provider import (
    OpenIDConnectProviderAccount,
)
from tests.apps.socialaccount.base import OpenIDConnectTests


class OpenIDConnectFetchUserInfoTests(OpenIDConnectTests, TestCase):
    provider_id = "oidc-server"


class OpenIDConnectUseIDTokenTests(OpenIDConnectTests, TestCase):
    provider_id = "other-oidc-server"

    def setup_provider(self):
        super().setup_provider()
        self.app.settings["fetch_userinfo"] = False
        self.app.save()
        self.extra_data = self.id_token


@pytest.mark.parametrize(
    "extra_data,expected_to_str",
    [
        ({"username": "compatpre6511"}, "compatpre6511"),
        ({"id_token": {"username": "idtokusr"}}, "idtokusr"),
        ({"userinfo": {"username": "userinfousr"}}, "userinfousr"),
    ],
)
def test_socialaccount_extra_data(extra_data, expected_to_str):
    sa = SocialAccount()
    sa.extra_data = extra_data
    assert OpenIDConnectProviderAccount(sa).to_str() == expected_to_str
