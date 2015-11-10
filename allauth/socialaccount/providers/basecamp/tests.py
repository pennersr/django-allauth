from allauth.socialaccount.tests import create_oauth2_tests
from allauth.tests import MockedResponse
from allauth.socialaccount.providers import registry

from .provider import BasecampProvider


class BasecampTests(create_oauth2_tests(registry.by_id(BasecampProvider.id))):
    def get_mocked_response(self):
        return MockedResponse(200, """
        {
            "expires_at": "2012-03-22T16:56:48-05:00",
            "identity": {
                "id": 9999999,
                "first_name": "Jason Fried",
                "last_name": "Jason Fried",
                "email_address": "jason@basecamp.com"
            },
            "accounts": [
                {
                    "product": "bcx",
                    "id": 88888888,
                    "name": "Wayne Enterprises, Ltd.",
                    "href": "https://basecamp.com/88888888/api/v1"
                },
                {
                    "product": "bcx",
                    "id": 77777777,
                    "name": "Veidt, Inc",
                    "href": "https://basecamp.com/77777777/api/v1"
                },
                {
                    "product": "campfire",
                    "id": 44444444,
                    "name": "Acme Shipping Co.",
                    "href": "https://acme4444444.campfirenow.com"
                }
            ]
        }""")
