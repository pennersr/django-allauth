# -*- coding: utf-8 -*-

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

    @property
    def authorize_url(self):
        return "{0}/protocol/openid-connect/auth".format(
            self.get_provider().provider_base_url
        )

    @property
    def access_token_url(self):
        return "{0}/protocol/openid-connect/token".format(
            self.get_provider().base_server_url
        )

    @property
    def profile_url(self):
        return "{0}/protocol/openid-connect/userinfo".format(
            self.get_provider().base_server_url
        )


def oauth2_login(request):
    view = OAuth2LoginView.adapter_view(
        KeycloakOAuth2Adapter(request, KeycloakProvider.id)
    )
    return view(request)


def oauth2_callback(request):
    view = OAuth2CallbackView.adapter_view(
        KeycloakOAuth2Adapter(request, KeycloakProvider.id)
    )
    return view(request)
