from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import CoinbaseProvider


class CoinbaseTests(OAuth2TestsMixin, TestCase):
    provider_id = CoinbaseProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """{
          "id": "9da7a204-544e-5fd1-9a12-61176c5d4cd8",
          "name": "User One",
          "username": "user1",
          "email": "user1@example.com",
          "profile_location": null,
          "profile_bio": null,
          "profile_url": "https://coinbase.com/user1",
          "avatar_url": "https://images.coinbase.com/avatar?h=vR%2FY8igBoPwuwGren5JMwvDNGpURAY%2F0nRIOgH%2FY2Qh%2BQ6nomR3qusA%2Bh6o2%0Af9rH&s=128",
          "resource": "user",
          "resource_path": "/v2/user"
            }""",
        )

    def get_expected_to_str(self):
        return "user1"
