from django.test import TestCase
from django.test.utils import override_settings

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse

from .provider import GlobusProvider


class GlobusTests(OAuth2TestsMixin, TestCase):
    provider_id = GlobusProvider.id

    @override_settings(SOCIALACCOUNT_QUERY_EMAIL=True)
    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
        {
            "identity_provider_display_name": "University of Gozorpazorp",
            "sub": "a6fc81e-4a6c1-97ac-b4c6-84ff6a8ce662",
            "preferred_username": "morty@ugz.edu",
            "identity_provider": "9a4c8312f-9432-9a7c-1654-6a987c6531fa",
            "organization": "University of Gozorpazorp",
            "email": "morty@ugz.edu",
            "name": "Morty Smith"
        }
        """,
        )

    def get_expected_to_str(self):
        return "morty@ugz.edu"
