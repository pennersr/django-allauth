from django.test import override_settings
from allauth.socialaccount.providers.oauth2.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase
from .provider import EbayProvider


class EBayTests(OAuth2TestsMixin, TestCase):
    provider_id = EbayProvider.id

    def setUp(self):
        self.app = SocialApp.objects.create(
            provider=EbayProvider.id,
            name="eBay",
            client_id="test-client-id",
            secret="test-secret",
        )

    def get_mocked_response(self, account_type="business"):
        if account_type == "business":
            response_content = """
            {
                "userId": "businessUser",
                "username": "Business User",
                "accountType": "BUSINESS",
                "businessAccount": {
                    "email": "businessuser@example.com"
                }
            }
            """
        else:
            response_content = """
            {
                "userId": "individualUser",
                "username": "Indivudal User",
                "accountType": "INDIVIDUAL",
                "individualAccount": {
                    "email": "studentuser@example.com"
                }
            }
            """
        return MockedResponse(200, response_content)

    @override_settings(EBAY_ENVIRONMENT="sandbox")
    def test_login_sandbox(self):
        response = self.client.get(reverse("ebay_login"))
        self.assertEqual(
            response.status_code, 302
        )  # Assuming a redirect to the eBay auth page

    @override_settings(EBAY_ENVIRONMENT="production")
    def test_login_production(self):
        response = self.client.get(reverse("ebay_login"))
        self.assertEqual(
            response.status_code, 302
        )  # Assuming a redirect to the eBay auth page

    def test_account_data_extraction(self):
        for account_type in ["business", "student"]:
            mocked_response = self.get_mocked_response(account_type)
            self.assertEqual(
                self.provider.extract_common_fields(mocked_response.json()),
                {
                    "userId": f"{account_type}User",
                    "username": f"{account_type.capitalize()} User",
                    "accountType": account_type.upper(),
                    "email": f"{account_type}user@example.com",
                },
            )
