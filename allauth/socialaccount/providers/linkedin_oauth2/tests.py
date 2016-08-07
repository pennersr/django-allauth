from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import LinkedInOAuth2Provider


class LinkedInOAuth2Tests(OAuth2TestsMixin, TestCase):
    provider_id = LinkedInOAuth2Provider.id

    def get_mocked_response(self):
        return MockedResponse(200, """
{
  "emailAddress": "raymond.penners@intenct.nl",
  "firstName": "Raymond",
  "id": "ZLARGMFT1M",
  "lastName": "Penners",
  "pictureUrl": "http://m.c.lnkd.licdn.com/mpr/mprx/0_e0hbvSLc",
  "publicProfileUrl": "http://www.linkedin.com/in/intenct"
}
""")
