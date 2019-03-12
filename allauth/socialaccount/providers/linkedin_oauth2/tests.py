from allauth.socialaccount.models import SocialAccount
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

    def test_data_to_str(self):
        data = {
            'emailAddress': 'john@doe.org',
            'firstName': 'John',
            'id': 'a1b2c3d4e',
            'lastName': 'Doe',
            'pictureUrl': 'https://media.licdn.com/mpr/foo',
            'pictureUrls': {'_total': 1,
                            'values': ['https://media.licdn.com/foo']},
            'publicProfileUrl': 'https://www.linkedin.com/in/johndoe'}
        acc = SocialAccount(extra_data=data, provider='linkedin_oauth2')
        self.assertEqual(acc.get_provider_account().to_str(), 'John Doe')
