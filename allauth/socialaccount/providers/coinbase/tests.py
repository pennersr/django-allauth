from allauth.socialaccount.tests import create_oauth2_tests
from allauth.tests import MockedResponse
from allauth.socialaccount.providers import registry

from .provider import CoinbaseProvider

class CoinbaseTests(create_oauth2_tests(registry.by_id(CoinbaseProvider.id))):
    def get_mocked_response(self):
        return MockedResponse(200, """
        {
            "users" : [
                        {
                            "user": {
                                "id": "123456",
                                "name": "Jane Doe",
                                "email": "janedoe@coinbase.com"
                            }
                        }
            ]
        }
        """)
