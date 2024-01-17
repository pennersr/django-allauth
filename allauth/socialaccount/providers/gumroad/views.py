# -*- coding: utf-8 -*-
from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.gumroad.provider import GumroadProvider
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class GumroadOauth2Adapter(OAuth2Adapter):
    provider_id = GumroadProvider.id
    supports_state = True

    settings = app_settings.PROVIDERS.get(provider_id, {})
    provider_base_url = settings.get("GUMROAD_URL")
    access_token_url = "{0}/oauth/token".format(provider_base_url)
    authorize_url = "{0}/oauth/authorize".format(provider_base_url)
    profile_url = "https://api.gumroad.com/v2/user"

    def complete_login(self, request, app, token, response):
        resp = (
            get_adapter()
            .get_requests_session()
            .get(self.profile_url, params={"access_token": token.token})
        )
        resp.raise_for_status()
        extra_data = resp.json()

        return self.get_provider().sociallogin_from_response(
            request, extra_data["user"]
        )


oauth2_login = OAuth2LoginView.adapter_view(GumroadOauth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(GumroadOauth2Adapter)
