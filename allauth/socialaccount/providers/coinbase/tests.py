from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import CoinbaseProvider


class CoinbaseTests(OAuth2TestsMixin, TestCase):
    provider_id = CoinbaseProvider.id

    def get_mocked_response(self):
        return MockedResponse(200, """


{
    {
  "data": [
    {
      "id": "58542935-67b5-56e1-a3f9-42686e07fa40",
      "name": "My Vault",
      "primary": false,
      "type": "vault",
      "currency": "BTC",
      "balance": {
        "amount": "4.00000000",
        "currency": "BTC"
      },
      "created_at": "2015-01-31T20:49:02Z",
      "updated_at": "2015-01-31T20:49:02Z",
      "resource": "account",
      "resource_path": "/v2/accounts/58542935-67b5-56e1-a3f9-42686e07fa40",
      "ready": true
    },
    {
      "id": "2bbf394c-193b-5b2a-9155-3b4732659ede",
      "name": "My Wallet",
      "primary": true,
      "type": "wallet",
      "currency": "BTC",
      "balance": {
        "amount": "39.59000000",
        "currency": "BTC"
      },
      "created_at": "2015-01-31T20:49:02Z",
      "updated_at": "2015-01-31T20:49:02Z",
      "resource": "account",
      "resource_path": "/v2/accounts/2bbf394c-193b-5b2a-9155-3b4732659ede"
    }
    ]
  }
}
        """)


