"""
Run just this suite:
python manage.py test allauth.socialaccount.providers.trainingpeaks.tests.TrainingPeaksTests
"""

from collections import namedtuple

from django.test import TestCase
from django.test.utils import override_settings

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse

from .provider import TrainingPeaksProvider
from .views import TrainingPeaksOAuth2Adapter


class TrainingPeaksTests(OAuth2TestsMixin, TestCase):
    provider_id = TrainingPeaksProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """{
                "Id": 123456,
                "FirstName": "John",
                "LastName": "Doe",
                "Email": "user@example.com",
                "DateOfBirth": "1986-02-01T00:00:00",
                "CoachedBy": 987654,
                "Weight": 87.5223617553711
            }""",
        )  # noqa

    def get_expected_to_str(self):
        return "user@example.com"

    def get_login_response_json(self, with_refresh_token=True):
        rtoken = ""
        if with_refresh_token:
            rtoken = ',"refresh_token": "testrf"'
        return (
            """{
                "access_token" : "testac",
                "token_type" : "bearer",
                "expires_in" : 600,
                "scope": "scopes granted"
            %s }"""
            % rtoken
        )

    def test_default_use_sandbox_uri(self):
        adapter = TrainingPeaksOAuth2Adapter(None)
        self.assertTrue(".sandbox." in adapter.authorize_url)
        self.assertTrue(".sandbox." in adapter.access_token_url)
        self.assertTrue(".sandbox." in adapter.profile_url)

    @override_settings(
        SOCIALACCOUNT_PROVIDERS={"trainingpeaks": {"USE_PRODUCTION": True}}
    )
    def test_use_production_uri(self):
        adapter = TrainingPeaksOAuth2Adapter(None)
        self.assertFalse(".sandbox." in adapter.authorize_url)
        self.assertFalse(".sandbox." in adapter.access_token_url)
        self.assertFalse(".sandbox." in adapter.profile_url)

    def test_scope_from_default(self):
        Request = namedtuple("request", ["GET"])
        mock_request = Request(GET={})
        scope = self.provider.get_scope_from_request(mock_request)
        self.assertTrue("athlete:profile" in scope)

    @override_settings(
        SOCIALACCOUNT_PROVIDERS={
            "trainingpeaks": {"SCOPE": ["athlete:profile", "workouts", "workouts:wod"]}
        }
    )
    def test_scope_from_settings(self):
        Request = namedtuple("request", ["GET"])
        mock_request = Request(GET={})
        scope = self.provider.get_scope_from_request(mock_request)
        for item in ("athlete:profile", "workouts", "workouts:wod"):
            self.assertTrue(item in scope)
