from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import PaypalProvider


class PaypalTests(OAuth2TestsMixin, TestCase):
    provider_id = PaypalProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
        {
            "user_id":
            "https://www.paypal.com/webapps/auth/server/64ghr894040044",
            "name": "Jane Doe",
            "given_name": "Jane",
            "family_name": "Doe",
            "email": "janedoe@example.com"
        }
        """,
        )

    def get_expected_to_str(self):
        return "janedoe@example.com"
