from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.tests import OAuthTestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import OpenStreetMapProvider


class OpenStreetMapTests(OAuthTestsMixin, TestCase):
    provider_id = OpenStreetMapProvider.id

    def get_mocked_response(self):
        return [
            MockedResponse(
                200,
                r"""
{
  "version": "0.6",
  "generator": "OpenStreetMap server",
  "copyright": "OpenStreetMap and contributors",
  "attribution": "http://www.openstreetmap.org/copyright",
  "license": "http://opendatacommons.org/licenses/odbl/1-0/",
  "user": {
    "id": 1,
    "display_name": "Steve",
    "account_created": "2024-11-06T20:11:01Z",
    "description": "",
    "contributor_terms": {
      "agreed": true,
      "pd": true
    },
    "img": {
      "href": "https://secure.gravatar.com/avatar.jpg"
    },
    "roles": [],
    "changesets": {
      "count": 0
    },
    "traces": {
      "count": 0
    },
    "blocks": {
      "received": {
        "count": 0,
        "active": 0
      }
    },
    "languages": [
      "en-US",
      "en"
    ],
    "messages": {
      "received": {
        "count": 0,
        "unread": 0
      },
      "sent": {
        "count": 0
      }
    }
  }
}
""",
            )
        ]  # noqa

    def get_expected_to_str(self):
        return "Steve"

    def test_login(self):
        super().test_login()
        account = SocialAccount.objects.get(uid="1")
        osm_account = account.get_provider_account()
        self.assertEqual(osm_account.get_username(), "Steve")
        self.assertEqual(
            osm_account.get_avatar_url(),
            "https://secure.gravatar.com/avatar.jpg",
        )
        self.assertEqual(
            osm_account.get_profile_url(),
            "https://www.openstreetmap.org/user/Steve",
        )
        self.assertEqual(osm_account.to_str(), "Steve")
