"""Test Eventbrite OAuth2 v3 Flow."""

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import EventbriteProvider


class EventbriteTests(OAuth2TestsMixin, TestCase):
    """Test Class for Eventbrite OAuth2 v3."""

    provider_id = EventbriteProvider.id

    def get_mocked_response(self):
        """Test authentication with an non-null image_id"""
        return MockedResponse(
            200,
            """{
            "emails": [{
                "email": "test@example.com",
                "verified": true
            }],
            "id": "999999999",
            "name": "Andrew Godwin",
            "first_name": "Andrew",
            "last_name": "Godwin",
            "image_id": "99999999"
        }""",
        )
