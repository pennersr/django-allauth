from allauth.socialaccount.tests import create_oauth2_tests
from allauth.tests import MockedResponse
from allauth.socialaccount.providers import registry

from .provider import AmazonProvider


class AmazonTests(create_oauth2_tests(registry.by_id(AmazonProvider.id))):
    def get_mocked_response(self):
        return MockedResponse(200, """
        {
          "Profile":{
                        "CustomerId":"amzn1.account.K2LI23KL2LK2",
                        "Name":"John Doe",
                        "PrimaryEmail":"johndoe@gmail.com"
                    }
        }""")
