"""Test Eventbrite OAuth2 v3 Flow."""

from django.test import TestCase

from allauth.socialaccount.providers.eventbrite.provider import EventbriteProvider
from tests.apps.socialaccount.base import OAuth2TestsMixin
from tests.mocking import MockedResponse


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

    def get_expected_to_str(self):
        return "test@example.com"
