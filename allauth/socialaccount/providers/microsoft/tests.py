import json

from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import MicrosoftGraphProvider
from .views import _check_errors


class MicrosoftGraphTests(OAuth2TestsMixin, TestCase):
    provider_id = MicrosoftGraphProvider.id

    def get_mocked_response(self):
        response_data = """
        {
            "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users/$entity",
            "id": "16f5a7b6-5a15-4568-aa5a-31bb117e9967",
            "businessPhones": [],
            "displayName": "Anne Weiler",
            "givenName": "Anne",
            "jobTitle": "Manufacturing Lead",
            "mail": "annew@CIE493742.onmicrosoft.com",
            "mobilePhone": "+1 3528700812",
            "officeLocation": null,
            "preferredLanguage": "en-US",
            "surname": "Weiler",
            "userPrincipalName": "annew@CIE493742.onmicrosoft.com"
        }
        """  # noqa
        return MockedResponse(200, response_data)

    def test_invalid_data(self):
        response = MockedResponse(200, json.dumps({}))
        with self.assertRaises(OAuth2Error):
            # No id, raises
            _check_errors(response)

    def test_profile_invalid_response(self):
        data = {
            "error": {
                "code": "InvalidAuthenticationToken",
                "message": "Access token validation failure. Invalid audience.",
            }
        }
        response = MockedResponse(401, json.dumps(data))

        with self.assertRaises(OAuth2Error):
            # no id, 4xx code, raises with message
            _check_errors(response)

    def test_invalid_response(self):
        response = MockedResponse(200, "invalid json data")
        with self.assertRaises(OAuth2Error):
            # bad json, raises
            _check_errors(response)
