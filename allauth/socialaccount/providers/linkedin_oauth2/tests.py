from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import LinkedInOAuth2Provider


class LinkedInOAuth2Tests(OAuth2TestsMixin, TestCase):
    provider_id = LinkedInOAuth2Provider.id

    def get_mocked_response(self):
        return MockedResponse(200, """
{
  "profilePicture": {
    "displayImage": "urn:li:digitalmediaAsset:12345abcdefgh-12abcd"
  },
  "id": "1234567",
  "lastName": {
    "preferredLocale": {
      "language": "en",
      "country": "US"
    },
    "localized": {
      "en_US": "Penners"
    }
  },
  "firstName": {
    "preferredLocale": {
      "language": "en",
      "country": "US"
    },
    "localized": {
      "en_US": "Raymond"
    }
  }
}
""")
