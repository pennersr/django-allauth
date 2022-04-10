from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import UNiDAYSProvider


class UNiDAYSTests(OAuth2TestsMixin, TestCase):
    provider_id = UNiDAYSProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
            {
                "sub": "4NCxvUBEuKAamihzsJp/T0ozD881fM8bQUGLFjz5zz4=",
                "given_name": "John",
                "family_name": "Smith",
                "email": john.smith1234@gmail.com,
                "verification_status":{
                    "verified" : true,
                    "user_type" : "student"
                }
            }
        """,
        )

    def get_login_response_json(self, with_refresh_token=True):
        return """
        { 
            "access_token" : "cf2b1462b99cc64992670b670bd82", 
            "token_type": "Bearer", 
            "expires_in" : 3600, 
            "refresh_token": "ad2b1874b99cc64992643d670bd82",  
        }
        """
