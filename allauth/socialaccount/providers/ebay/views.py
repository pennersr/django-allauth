# -*- coding: utf-8 -*-
import requests

from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.ebay.provider import EBayProvider
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class EBayOAuth2Adapter(OAuth2Adapter):
    provider_id = EBayProvider.id
    production_access_token_url = "https://api.ebay.com/identity/v1/oauth2/token"
    sandbox_access_token_url = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
    production_authorize_url = "https://auth.ebay.com/oauth2/authorize"
    sandbox_authorize_url = "https://auth.sandbox.ebay.com/oauth2/authorize"

    grant_type = "authorization_code"
    scope = ["https://api.ebay.com/oauth/api_scope"]

    supports_state = False

    def complete_login(self, request, app, token, **kwargs):
        headers = {
            "Authorization": f"Bearer {token.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        resp = requests.get("https://api.ebay.com/oauth/api_scope", headers=headers)

        resp.raise_for_status()
        data = resp.json()
        return self.get_provider().sociallogin_from_response(request, data)

    def get_access_token_url(self, request, app):
        return (
            self.production_access_token_url
            if app.sandbox
            else self.sandbox_access_token_url
        )

    def get_authorize_url(self, request, app):
        return (
            self.production_authorize_url
            if not app.sandbox
            else self.sandbox_authorize_url
        )


oauth2_login = OAuth2LoginView.adapter_view(EBayOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(EBayOAuth2Adapter)
