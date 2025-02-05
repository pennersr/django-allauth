from django.test import TestCase

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse

from .provider import SlackProvider


class SlackOAuth2Tests(OAuth2TestsMixin, TestCase):
    provider_id = SlackProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """{
    "ok": true,
    "sub": "U0R7JM",
    "https://slack.com/user_id": "U0R7JM",
    "https://slack.com/team_id": "T0R7GR",
    "email": "krane@slack-corp.com",
    "email_verified": true,
    "date_email_verified": 1622128723,
    "name": "krane",
    "picture": "https://secure.gravatar.com/....png",
    "given_name": "Bront",
    "family_name": "Labradoodle",
    "locale": "en-US",
    "https://slack.com/team_name": "kraneflannel",
    "https://slack.com/team_domain": "kraneflannel"
        }""",
        )  # noqa

    def get_expected_to_str(self):
        return "krane@slack-corp.com"
