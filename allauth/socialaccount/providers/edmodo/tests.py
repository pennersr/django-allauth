from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import EdmodoProvider


class EdmodoTests(OAuth2TestsMixin, TestCase):
    provider_id = EdmodoProvider.id

    def get_mocked_response(self):
        return MockedResponse(200, """
{
  "url": "https://api.edmodo.com/users/74721257",
  "id": 74721257,
  "type": "teacher",
  "username": "getacclaim-teacher1",
  "user_title": null,
  "first_name": "Edmodo Test",
  "last_name": "Teacher",
  "time_zone": "America/New_York",
  "utc_offset": -18000,
  "locale": "en",
  "gender": null,
  "start_level": null,
  "end_level": null,
  "about": null,
  "premium": false,
  "school": {"url": "https://api.edmodo.com/schools/559253", "id": 559253},
  "verified_institution_member": true,
  "coppa_verified": false,
  "subjects": null,
  "avatars": {
    "small": "https://api.edmodo.com/users/74721257/avatar?type=small&u=670329ncqnf8fxv7tya24byn5",
    "large": "https://api.edmodo.com/users/74721257/avatar?type=large&u=670329ncqnf8fxv7tya24byn5"
  },
  "email":"test@example.com",
  "sync_enabled": false
}
""")
