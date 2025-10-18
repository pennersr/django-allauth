from http import HTTPStatus

from django.test import TestCase

from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.discogs.provider import DiscogsProvider
from tests.apps.socialaccount.base import OAuthTestsMixin
from tests.mocking import MockedResponse


class DiscogsTests(OAuthTestsMixin, TestCase):
    provider_id = DiscogsProvider.id

    def get_mocked_response(self):
        return [
            MockedResponse(
                HTTPStatus.OK,
                r'{"id": 5788917, "username": "veljkoj", '
                r'"resource_url": "https://api.discogs.com/users/veljkoj", '
                r'"consumer_name": "myapp"}',
            )
        ]

    def get_expected_to_str(self):
        return "veljkoj"

    def test_login(self):
        super().test_login()
        account = SocialAccount.objects.get(uid="5788917")
        discogs_account = account.get_provider_account()

        self.assertEqual(discogs_account.get_username(), "veljkoj")
        self.assertEqual(
            discogs_account.get_profile_url(),
            r"https://api.discogs.com/users/veljkoj",
        )
        self.assertEqual(discogs_account.to_str(), "veljkoj")
