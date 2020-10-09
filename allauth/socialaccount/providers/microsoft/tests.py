from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import MicrosoftGraphProvider


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
