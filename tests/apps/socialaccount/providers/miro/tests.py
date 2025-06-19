from django.test import TestCase

from allauth.socialaccount.providers.miro.provider import MiroProvider
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse


class MiroTests(OAuth2TestsMixin, TestCase):
    provider_id = MiroProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """{
                "type" : "user",
                "id" : "5298357290348572584",
                "name" : "Pavel Oborin",
                "createdAt" : "2017-03-23T09:41:01Z",
                "role" : "developer",
                "email" : "oborin.p@gmail.com",
                "state" : "registered",
                "picture" : {
                    "type" : "picture",
                    "id" : "Optional[5289752983457238457]",
                    "imageUrl" : "https://r.miro.com/some/image"
                }
            }""",
        )

    def get_expected_to_str(self):
        return "oborin.p@gmail.com"
