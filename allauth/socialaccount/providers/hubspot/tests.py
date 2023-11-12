from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import HubspotProvider


class HubspotTests(OAuth2TestsMixin, TestCase):
    provider_id = HubspotProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """{
                    "token": "CNye4dqFMBICAAEYhOKlDZZ_z6IVKI_xMjIUgmFsNQzgBjNE9YBmhAhNOtfN0ak6BAAAAEFCFIIwn2EVRLpvJI9hP4tbIeKHw7ZXSgNldTFSAFoA",
                    "user": "m@acme.com",
                    "hub_domain": "acme.com",
                    "scopes": ["oauth"],
                    "scope_to_scope_group_pks": [25, 31],
                    "trial_scopes": [],
                    "trial_scope_to_scope_group_pks": [],
                    "hub_id": 211580,
                    "app_id": 833572,
                    "expires_in": 1799,
                    "user_id": 42607123,
                    "token_type": "access"
                }""",
        )
