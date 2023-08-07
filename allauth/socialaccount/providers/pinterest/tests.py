from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import PinterestProvider


class PinterestTests(OAuth2TestsMixin, TestCase):
    provider_id = PinterestProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
        {
            "data": {
                "url": "https://www.pinterest.com/muravskiyyarosl/",
                "first_name": "Jane",
                "last_name": "Doe",
                "id": "351247977031674143"
            }
        }
        """,
        )
