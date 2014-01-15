from allauth.socialaccount.tests import create_oauth2_tests
from allauth.tests import MockedResponse
from allauth.socialaccount.providers import registry

from .provider import PaypalProvider

class PaypalTests(create_oauth2_tests(registry.by_id(PaypalProvider.id))):
    def get_mocked_response(self):
        return MockedResponse(200, """
        {
            "user_id": "https://www.paypal.com/webapps/auth/server/64ghr894040044",
            "name": "Jane Doe",
            "given_name": "Jane",
            "family_name": "Doe",
            "email": "janedoe@paypal.com"
        }
        """)
