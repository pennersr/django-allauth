"""Test MailChimp OAuth2 v3 Flow."""

from django.test import TestCase

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse

from .provider import MailChimpProvider


class MailChimpTests(OAuth2TestsMixin, TestCase):
    """Test Class for MailChimp OAuth2 v3."""

    provider_id = MailChimpProvider.id

    def get_mocked_response(self):
        """Test authentication with an non-null avatar."""
        return MockedResponse(
            200,
            """{
            "dc": "usX",
            "role": "owner",
            "accountname": "Name can have spaces",
            "user_id": "99999999",
            "login": {
                "email": "test@example.com",
                "avatar": "http://gallery.mailchimp.com/1a1a/avatar/2a2a.png",
                "login_id": "88888888",
                "login_name": "test@example.com",
                "login_email": "test@example.com"
            },
            "login_url": "https://login.mailchimp.com",
            "api_endpoint": "https://usX.api.mailchimp.com"
        }""",
        )

    def get_expected_to_str(self):
        return "test@example.com"
