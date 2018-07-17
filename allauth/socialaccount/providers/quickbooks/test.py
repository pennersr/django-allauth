from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import QuickBooksOAuth2Provider


class QuickBooksOAuth2Tests(OAuth2TestsMixin, TestCase):
    provider_id = QuickBooksOAuth2Provider.id

    def get_mocked_response(self):
        return MockedResponse(200, """
{       "sub": "d8752092-0f2b-4b6e-86ef-6b72f2457a00",
        "emailVerified": true,
        "familyName": "Mckeeman",
        "phoneNumber": "+1 4156694355",
        "givenName": "Darren",
        "phoneNumberVerified": true,
        "email": "darren@blocklight.io"}
""")
