from http import HTTPStatus

from django.test import TestCase

from allauth.socialaccount.providers.clever.provider import CleverProvider
from tests.apps.socialaccount.base import OAuth2TestsMixin
from tests.mocking import MockedResponse


class CleverOAuth2Tests(OAuth2TestsMixin, TestCase):
    provider_id = CleverProvider.id

    def get_mocked_response(self):
        return [
            MockedResponse(
                HTTPStatus.OK,
                """{
            "type": "user",
            "data": {
                "id": "62027798269867124d10259e",
                "district": "6202763c8243d2100123dae5",
                "type": "user",
                "authorized_by": "district"
            },
            "links": [
                {
                "rel": "self",
                "uri": "/me"
                },
                {
                "rel": "canonical",
                "uri": "/v3.0/users/62027798269867124d10259e"
                },
                {
                "rel": "district",
                "uri": "/v3.0/districts/6202763c8243d2100123dae5"
                }
            ]
        }""",
            ),
            MockedResponse(
                HTTPStatus.OK,
                """{
                "data": {
                "id": "62027798269867124d10259e",
                  "roles": {
                "district_admin": {},
                "contact": {}
                }
                }
                }""",
            ),
        ]

    def get_expected_to_str(self):
        return "Clever"
