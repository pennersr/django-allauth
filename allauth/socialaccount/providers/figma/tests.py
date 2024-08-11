from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import FigmaProvider


class FigmaTests(OAuth2TestsMixin, TestCase):
    provider_id = FigmaProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
                {
                  "id": "2600",
                  "email": "johndoe@example.com",
                  "handle": "John Doe",
                  "img_url": "https://www.example.com/image.png"
                }
            """,
        )

    def get_expected_to_str(self):
        return "John Doe"
