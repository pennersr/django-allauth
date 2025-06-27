from django.test import TestCase

from allauth.socialaccount.providers.paypal.provider import PaypalProvider
from tests.apps.socialaccount.base import OAuth2TestsMixin
from tests.mocking import MockedResponse


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
