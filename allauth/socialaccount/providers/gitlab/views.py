# -*- coding: utf-8 -*-
import requests

from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.gitlab.provider import GitLabProvider
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class GitLabOAuth2Adapter(OAuth2Adapter):
    provider_id = GitLabProvider.id
    provider_default_url = 'https://gitlab.com'
    provider_api_version = 'v3'

    settings = app_settings.PROVIDERS.get(provider_id, {})
    provider_base_url = settings.get('GITLAB_URL', provider_default_url)

    access_token_url = '{0}/oauth/token'.format(provider_base_url)
    authorize_url = '{0}/oauth/authorize'.format(provider_base_url)
    profile_url = '{0}/api/{1}/user'.format(
        provider_base_url, provider_api_version
    )

    def complete_login(self, request, app, token, response):
        extra_data = requests.get(self.profile_url, params={
            'access_token': token.token
        })

        return self.get_provider().sociallogin_from_response(
            request,
            extra_data.json()
        )


oauth2_login = OAuth2LoginView.adapter_view(GitLabOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(GitLabOAuth2Adapter)
