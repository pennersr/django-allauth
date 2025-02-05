from django.test import TestCase
from django.test.utils import override_settings

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse

from .provider import NextCloudProvider


@override_settings(
    SOCIALACCOUNT_PROVIDERS={"nextcloud": {"SERVER": "https://nextcloud.example.org"}}
)
class NextCloudTests(OAuth2TestsMixin, TestCase):
    provider_id = NextCloudProvider.id

    def get_login_response_json(self, with_refresh_token=True):
        return (
            super(NextCloudTests, self)
            .get_login_response_json(with_refresh_token=with_refresh_token)
            .replace("uid", "user_id")
        )

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
{
  "ocs": {
    "meta": {
      "status": "ok",
      "statuscode": 100,
      "message": "OK",
      "totalitems": "",
      "itemsperpage": ""
    },
    "data": {
      "enabled": true,
      "storageLocation": "\\/var\\/www\\/html\\/data\\/pennersr",
      "id": "pennersr",
      "lastLogin": 1730973409000,
      "backend": "Database",
      "subadmin": [],
      "quota": {
        "free": 9159623057408,
        "used": 1585107741,
        "total": 9161208165149,
        "relative": 0.02,
        "quota": -3
      },
      "email": "batman@wayne.com",
      "displayname": "pennersr",
      "phone": "",
      "address": "",
      "website": "",
      "twitter": "",
      "groups": [
        "admin"
      ],
      "language": "nl",
      "locale": ""
    }
  }
}
""",
        )

    def get_expected_to_str(self):
        return "batman@wayne.com"
