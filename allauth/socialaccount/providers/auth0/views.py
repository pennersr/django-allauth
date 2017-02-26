# -*- coding: utf-8 -*-
import requests

from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.auth0.provider import Auth0Provider
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class Auth0OAuth2Adapter(OAuth2Adapter):
    provider_id = Auth0Provider.id
    supports_state = True

    settings = app_settings.PROVIDERS.get(provider_id, {})
    provider_base_url = settings.get("AUTH0_URL")

    access_token_url = '{0}/oauth/token'.format(provider_base_url)
    authorize_url = '{0}/authorize'.format(provider_base_url)
    profile_url = '{0}/userinfo'.format(provider_base_url)

    def complete_login(self, request, app, token, response):
        extra_data = requests.get(self.profile_url, params={
            'access_token': token.token
        }).json()
        extra_data = {
            'user_id': extra_data['user_id'],
            'id': extra_data['user_id'],
            'name': extra_data['name'],
            'email': extra_data['email']
        }

        return self.get_provider().sociallogin_from_response(
            request,
            extra_data
        )


oauth2_login = OAuth2LoginView.adapter_view(Auth0OAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(Auth0OAuth2Adapter)
