from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import ShareFileProvider


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
