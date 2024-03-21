# -*- coding: utf-8 -*-
import requests

from django.conf import settings

# from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.ebay.provider import EBayProvider
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2LoginView,
    OAuth2CallbackView,
)
from .provider import eBayProvider


class eBayOAuth2Adapter(OAuth2Adapter):
    provider_id = eBayProvider.id

    def __init__(self, request):
        self.access_token_url = self.get_base_url() + "identity/v1/oauth2/token"
        self.authorize_url = self.get_base_url() + "identity/v1/oauth2/authorize"
        self.profile_url = self.get_base_url() + "commerce/identity/v1/user/"
        # super().__init__(request)

    def get_environment(self):
        app = self.get_provider().app
        return app.settings.get("environment", "production")

    def get_base_url(self):
        environment = self.get_environment()
        if environment == "production":
            return "https://api.ebay.com/"
        else:
            return "https://api.sandbox.ebay.com/"

    def complete_login(self, request, app, token, **kwargs):
        headers = {
            "Authorization": f"Bearer {token.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        resp = requests.get(self.profile_url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        # resp = requests.get(
        #     "https://api.ebay.com/oauth/api_scope/identity", headers=headers
        # )

        # resp.raise_for_status()

        # data = resp.json()
        return self.get_provider().sociallogin_from_response(request, data)


oauth2_login = OAuth2LoginView.adapter_view(eBayOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(eBayOAuth2Adapter)
