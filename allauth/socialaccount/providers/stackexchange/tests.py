from django.test import TestCase

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse

from .provider import StackExchangeProvider


class StackExchangeTests(OAuth2TestsMixin, TestCase):
    provider_id = StackExchangeProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
        {
          "has_more": false,
           "items": [
              {
                "is_employee": false,
                 "last_access_date": 1356200390,
                 "display_name": "pennersr",
                 "account_id": 291652,
                 "badge_counts": {
                     "bronze": 2,
                     "silver": 2,
                     "gold": 0
                 },
                 "last_modified_date": 1356199552,
                 "profile_image":
                 "http://www.gravatar.com/avatar/053d648486d567d3143d6bad8df8cfeb?d=identicon&r=PG",
                 "user_type": "registered",
                 "creation_date": 1296223711,
                 "reputation_change_quarter": 148,
                 "reputation_change_year": 378,
                 "reputation": 504,
                 "link": "http://stackoverflow.com/users/593944/pennersr",
                 "reputation_change_week": 0,
                 "user_id": 593944,
                 "reputation_change_month": 10,
                 "reputation_change_day": 0
              }
           ],
           "quota_max": 10000,
           "quota_remaining": 9999
        }""",
        )  # noqa

    def get_expected_to_str(self):
        return "pennersr"
