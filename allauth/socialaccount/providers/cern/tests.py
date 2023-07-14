from allauth.socialaccount.tests import OpenIDConnectTests
from allauth.tests import MockedResponse, TestCase

from .provider import CernProvider


class CernTests(OpenIDConnectTests, TestCase):
    provider_id = CernProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
            {
                "exp": 9999999999,
                "iat": 9999999999,
                "auth_time": 9999999999,
                "jti": "Random",
                "iss": "https://auth.cern.ch/auth/realms/cern",
                "aud": "test-audience",
                "sub": "mmuster",
                "typ": "ID",
                "azp": "test-audience",
                "session_state": "Random",
                "at_hash": "Random",
                "sid": "Random",
                "resource_access": {
                    "test-audience": {
                        "roles": [
                            "default-role"
                        ]
                    }
                },
                "cern_person_id": "924225",
                "name": "Max Mustermann",
                "cern_mail_upn": "max.mustermann@cern.ch",
                "preferred_username": "mmuster",
                "given_name": "Max",
                "cern_roles": [
                    "default-role"
                ],
                "cern_preferred_language": "EN",
                "family_name": "Mustermann",
                "email": "max.mustermann@cern.ch",
                "cern_upn": "mmuster"
            }
            """,
        )
