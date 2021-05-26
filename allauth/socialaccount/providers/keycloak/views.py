# -*- coding: utf-8 -*-
import requests

from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.keycloak.provider import KeycloakProvider
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class KeycloakOAuth2Adapter(OAuth2Adapter):
    provider_id = KeycloakProvider.id
    supports_state = True

    settings = app_settings.PROVIDERS.get(provider_id, {})
    provider_base_url = "{0}/realms/{1}".format(
        settings.get("KEYCLOAK_URL"), settings.get("KEYCLOAK_REALM")
    )

    access_token_url = "{0}/protocol/openid-connect/token".format(provider_base_url)
    authorize_url = "{0}/protocol/openid-connect/auth".format(provider_base_url)
    profile_url = "{0}/protocol/openid-connect/userinfo".format(provider_base_url)

    def complete_login(self, request, app, token, response):
        response = requests.post(
            self.profile_url, headers={"Authorization": "Bearer " + str(token)}
        )
        response.raise_for_status()
        extra_data = response.json()
        extra_data["id"] = extra_data["sub"]
        del extra_data["sub"]

        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(KeycloakOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(KeycloakOAuth2Adapter)
