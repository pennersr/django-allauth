# -*- coding: utf-8 -*-

from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.keycloak.provider import KeycloakProvider
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2CallbackView,
    OAuth2LoginView,
)
from allauth.socialaccount.providers.openid_connect.views import (
    OpenIDConnectAdapter,
)


class KeycloakOAuth2Adapter(OpenIDConnectAdapter):
    provider_id = KeycloakProvider.id

    settings = app_settings.PROVIDERS.get(provider_id, {})
    provider_base_url = "{0}/realms/{1}".format(
        settings.get("KEYCLOAK_URL"), settings.get("KEYCLOAK_REALM")
    )

    authorize_url = "{0}/protocol/openid-connect/auth".format(provider_base_url)

    other_url = settings.get("KEYCLOAK_URL_ALT")
    if other_url is None:
        other_url = settings.get("KEYCLOAK_URL")

    server_base_url = "{0}/realms/{1}".format(other_url, settings.get("KEYCLOAK_REALM"))
    access_token_url = "{0}/protocol/openid-connect/token".format(server_base_url)
    profile_url = "{0}/protocol/openid-connect/userinfo".format(server_base_url)


oauth2_login = OAuth2LoginView.adapter_view(KeycloakOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(KeycloakOAuth2Adapter)
