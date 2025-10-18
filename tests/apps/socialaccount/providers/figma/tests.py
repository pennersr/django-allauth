from http import HTTPStatus

from django.test import TestCase

from allauth.socialaccount.providers.figma.provider import FigmaProvider
from tests.apps.socialaccount.base import OAuth2TestsMixin
from tests.mocking import MockedResponse


class FigmaTests(OAuth2TestsMixin, TestCase):
    provider_id = FigmaProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            HTTPStatus.OK,
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
