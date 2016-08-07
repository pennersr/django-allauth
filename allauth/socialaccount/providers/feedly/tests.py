from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import FeedlyProvider


class FeedlyTests(OAuth2TestsMixin, TestCase):
    provider_id = FeedlyProvider.id

    def get_mocked_response(self):
        return MockedResponse(200, """
{
  "id": "c805fcbf-3acf-4302-a97e-d82f9d7c897f",
  "email": "jim.smith@gmail.com",
  "givenName": "Jim",
  "familyName": "Smith",
  "picture": "https://www.google.com/profile_images/1771656873/bigger.jpg",
  "gender": "male",
  "locale": "en",
  "reader": "9080770707070700",
  "google": "115562565652656565656",
  "twitter": "jimsmith",
  "facebook": "",
  "wave": "2013.7"
}""")
