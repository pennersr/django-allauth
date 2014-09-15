from allauth.socialaccount.tests import create_oauth2_tests
from allauth.tests import MockedResponse
from allauth.socialaccount.providers import registry

from .provider import CoinbaseProvider

class CoinbaseTests(create_oauth2_tests(registry.by_id(CoinbaseProvider.id))):
    def get_mocked_response(self):
        return MockedResponse(200, """
{
  "users": [
    {
      "user": {
        "id": "512db383f8182bd24d000001",
        "name": "User One",
        "email": "user1@example.com",
        "time_zone": "Pacific Time (US & Canada)",
        "native_currency": "USD",
        "balance": {
          "amount": "49.76000000",
          "currency": "BTC"
        },
        "merchant": {
          "company_name": "Company Name, Inc.",
          "logo": {
            "small": "http://smalllogo.example",
            "medium": "http://mediumlogo.example",
            "url": "http://logo.example"
          }
        },
        "buy_level": 1,
        "sell_level": 1,
        "buy_limit": {
          "amount": "10.00000000",
          "currency": "BTC"
        },
        "sell_limit": {
          "amount": "100.00000000",
          "currency": "BTC"
        }
      }
    }
  ]
}
        """)
