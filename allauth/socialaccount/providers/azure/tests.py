from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import AzureProvider


class AzureTests(OAuth2TestsMixin, TestCase):
    provider_id = AzureProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
        {"displayName": "John Smith", "mobilePhone": null,
        "preferredLanguage": "en-US", "jobTitle": "Director",
        "userPrincipalName": "john@smith.com",
        "@odata.context":
        "https://graph.microsoft.com/v1.0/$metadata#users/$entity",
        "officeLocation": "Paris", "businessPhones": [],
        "mail": "john@smith.com", "surname": "Smith",
        "givenName": "John", "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"}
        """,
        )
