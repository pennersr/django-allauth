from http import HTTPStatus

from django.test import TestCase

from allauth.socialaccount.providers.trello.provider import TrelloProvider
from tests.apps.socialaccount.base import OAuthTestsMixin
from tests.mocking import MockedResponse


class TrelloTests(OAuthTestsMixin, TestCase):
    provider_id = TrelloProvider.id

    def get_mocked_response(self):
        return [
            MockedResponse(
                HTTPStatus.OK,
                r"""
{"id": "123", "email": "raymond.penners@example.com", "username": "pennersr", "name": "Raymond"}
        """,
            ),
        ]  # noqa

    def get_expected_to_str(self):
        return "pennersr"
