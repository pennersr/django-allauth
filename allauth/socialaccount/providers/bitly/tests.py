from django.test import TestCase

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse

from .provider import BitlyProvider


class BitlyTests(OAuth2TestsMixin, TestCase):
    provider_id = BitlyProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """{
            "data": {
                "apiKey": "R_f6397a37e765574f2e198dba5bb59522",
                "custom_short_domain": null,
                "display_name": null,
                "full_name": "Bitly API Oauth Demo Account",
                "is_enterprise": false,
                "login": "bitlyapioauthdemo",
                "member_since": 1331567982,
                "profile_image": "http://bitly.com/u/bitlyapioauthdemo.png",
                "profile_url": "http://bitly.com/u/bitlyapioauthdemo",
                "share_accounts": [],
                "tracking_domains": []
            },
            "status_code": 200,
            "status_txt": "OK"
        }""",
        )

    def get_expected_to_str(self):
        return "bitlyapioauthdemo"
