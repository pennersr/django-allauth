from django.test import TestCase

from allauth.socialaccount.providers.sharefile.provider import ShareFileProvider
from tests.apps.socialaccount.base import OAuth2TestsMixin
from tests.mocking import MockedResponse


class ShareFileTests(OAuth2TestsMixin, TestCase):
    provider_id = ShareFileProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
{
  "Id": "123",
  "Email":"user.one@domain.com",
  "FirstName":"Name",
  "LastName":"Last Name",
  "Company":"Company",
  "DefaultZone":
  {
    "Id":"zoneid"
  }
}         """,
        )

    def get_expected_to_str(self):
        return "user.one@domain.com"
