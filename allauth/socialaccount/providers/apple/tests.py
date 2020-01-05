from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import AppleProvider


class AppleTests(OAuth2TestsMixin, TestCase):
    provider_id = AppleProvider.id

    def get_mocked_response(self):
        return MockedResponse(200, """
{"iss": "https://appleid.apple.com", 
"aud": "ru.apple.signin", 
"exp": 1577627338, 
"iat": 1577626738, 
"sub": "000313.c9720f41e9434e18987a.1218", 
"at_hash": "CkaUPjk4MJinaAq6Z0tGUA", 
"email": "test@privaterelay.appleid.com", 
"email_verified": "true", 
"is_private_email": "true", 
"auth_time": 1577626731}
""")
