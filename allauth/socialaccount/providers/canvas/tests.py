from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import DigitalOceanProvider


class DigitalOceanTests(OAuth2TestsMixin, TestCase):
    provider_id = DigitalOceanProvider.id

    def get_mocked_response(self):
        # https://canvas.instructure.com/doc/api/users.html#Profile
        return MockedResponse(200, """
            {
              "id": 5670506,
              "name": "Grover Kingrey",
              "short_name": "Grover Kingrey",
              "sortable_name": "Kingrey, Grover",
              "avatar_url": "https://canvas.example.edu/images/messages/avatar-50.png",
              "title": null,
              "bio": null,
              "primary_email": "groverk@example.edu",
              "login_id": "groverk",
              "integration_id": null,
              "time_zone": "America/New_York",
              "locale": null,
              "effective_locale": "en",
              "calendar": {
                "ics": "https://canvas.example.edu/feeds/calendars/user_example.ics"
              }
            }
        """)

    def get_login_response_json(self, with_refresh_token=True):
        # https://canvas.instructure.com/doc/api/file.oauth_endpoints.html#post-login-oauth2-token
        return """{
          "access_token": "1/fFAGRNJru1FTz70BzhT3Zg",
          "token_type": "Bearer",
          "user": {"id":42, "name": "Jimi Hendrix"},
          "refresh_token": "tIh2YBWGiC0GgGRglT9Ylwv2MnTvy8csfGyfK2PqZmkFYYqYZ0wui4tzI7uBwnN2",
          "expires_in": 3600,
          "canvas_region": "us-east-1"
        }"""
