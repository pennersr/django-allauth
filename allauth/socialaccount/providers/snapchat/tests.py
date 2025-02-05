from django.test import TestCase

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse

from .provider import SnapchatProvider


class SnapchatOAuth2Tests(OAuth2TestsMixin, TestCase):
    provider_id = SnapchatProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """{
                  "data":{
                      "me":{
                        "externalId":"CAESIPiRBp0e5gLDq7VVurQ3rVdmdbqxpOJWynjyBL/xlo0w",
                        "displayName":"Karun Shrestha",
                        "bitmoji":{
                            "avatar":"https://sdk.bitmoji.com/render/panel/336d1e96-9055-4818-81aa-adde45ec030f-3aBXH5B0ZPCr~grPTZScjprXRT2RkU90oSd7X_PjDFFnBe3wuFkD1R-v1.png?transparent=1&palette=1",
                            "id":"3aBXH5B0ZPCr~grPTZScjprXRT2RkU90oSd7X_PjDFFnBe3wuFkD1R"
                        }
                      }
                  },
                  "errors":[]
            }""",
        )  # noqa

    def get_expected_to_str(self):
        return "Karun Shrestha"
