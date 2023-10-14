# -*- coding: utf-8 -*-
import requests

from django.conf import settings

# from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.ebay.provider import EBayProvider
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

ENVIRONMENTS = {
    "production": {
        "auth_url": "https://auth.ebay.com/oauth2/authorize",
        "token_url": "https://api.ebay.com/identity/v1/oauth2/token",
    },
    "sandbox": {
        "auth_url": "https://auth.sandbox.ebay.com/oauth2/authorize",
        "token_url": "https://api.sandbox.ebay.com/identity/v1/oauth2/token",
    },
}

ENV = (
    getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
    .get("ebay", {})
    .get("ENVIRONMENT", "production")
)

AUTH_URL = ENVIRONMENTS[ENV]["auth_url"]
TOKEN_URL = ENVIRONMENTS[ENV]["token_url"]


class EBayOAuth2Adapter(OAuth2Adapter):
    provider_id = EBayProvider.id
    access_token_url = TOKEN_URL
    authorize_url = AUTH_URL

    grant_type = "authorization_code"
    scope = ["https://api.ebay.com/oauth/api_scope"]

    supports_state = True

    def complete_login(self, request, app, token, **kwargs):
        headers = {
            "Authorization": f"Bearer {token.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        resp = requests.get(
            "https://api.ebay.com/oauth/api_scope/identity", headers=headers
        )

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            raise Exception(f"Error retrieving user data from eBay API: {resp.content}")

        data = resp.json()
        return self.get_provider().sociallogin_from_response(request, data)


oauth2_login = OAuth2LoginView.adapter_view(EBayOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(EBayOAuth2Adapter)
