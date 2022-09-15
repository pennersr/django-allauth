# -*- coding: utf-8 -*-
import requests

from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.keap.provider import KeapProvider
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class KeapOAuth2Adapter(OAuth2Adapter):
    provider_id = KeapProvider.id
    supports_state = True

    access_token_url = "https://api.infusionsoft.com/token"
    authorize_url = "https://accounts.infusionsoft.com/app/oauth/authorize"
    profile_url = "https://api.infusionsoft.com/crm/rest/v1/oauth/connect/userinfo"

    def complete_login(self, request, app, token, **kwargs):
        response = kwargs.get("response", None)
        scope = response.get("scope", "")
        app_name = scope.split("|")[1].split(".")[0]

        profile_response = requests.get(
            self.profile_url, params={"access_token": token.token}
        )
        profile_response.raise_for_status()
        extra_data = profile_response.json()
        extra_data["scope"] = response.get("scope")
        extra_data["app_name"] = app_name


oauth2_login = OAuth2LoginView.adapter_view(KeapOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(KeapOAuth2Adapter)
