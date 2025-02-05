from django.test import TestCase

from allauth.socialaccount.tests import OAuthTestsMixin
from allauth.tests import MockedResponse

from .provider import TrelloProvider


class TrelloTests(OAuthTestsMixin, TestCase):
    provider_id = TrelloProvider.id

    def get_mocked_response(self):
        return [
            MockedResponse(
                200,
                r"""
{"id": "123", "email": "raymond.penners@example.com", "username": "pennersr", "name": "Raymond"}
        """,
            ),
        ]  # noqa

    def get_expected_to_str(self):
        return "pennersr"
