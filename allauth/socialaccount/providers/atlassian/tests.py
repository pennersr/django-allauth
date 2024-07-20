from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import AtlassianProvider


class AtlassianTests(OAuth2TestsMixin, TestCase):
    provider_id = AtlassianProvider.id

    def get_mocked_response(self):
        response_data = """
        {
            "account_type": "atlassian",
            "account_id": "112233aa-bb11-cc22-33dd-445566abcabc",
            "email": "mia@example.com",
            "email_verified": true,
            "name": "Mia Krystof",
            "picture": "https://avatar-management--avatars.us-west-2.prod.public.atl-paas.net/112233aa-bb11-cc22-33dd-445566abcabc/1234abcd-9876-54aa-33aa-1234dfsade9487ds",
            "account_status": "active",
            "nickname": "mkrystof",
            "zoneinfo": "Australia/Sydney",
            "locale": "en-US",
            "extended_profile": {
                "job_title": "Designer",
                "organization": "mia@example.com",
                "department": "Design team",
                "location": "Sydney"
            }
        }"""
        return MockedResponse(200, response_data)

    def get_expected_to_str(self):
        return "mia@example.com"
