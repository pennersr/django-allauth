# -*- coding: utf-8 -*-
from allauth.socialaccount.providers.gitlab.provider import GitLabProvider
from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter
from allauth.socialaccount.providers.oauth2.views import OAuth2CallbackView
from allauth.socialaccount.providers.oauth2.views import OAuth2LoginView
from django.conf import settings

import requests


class GitLabOAuth2Adapter(OAuth2Adapter):
    provider_id = GitLabProvider.id

    access_token_url = getattr(
        settings, 'GITLAB_ACCESS_TOKEN_URL', 'https://gitlab.com/oauth/token'
    )

    authorize_url = getattr(
        settings, 'GITLAB_USER_AUTHORIZATION_URL', 'https://gitlab.com/oauth/authorize'  # noqa
    )

    profile_url = getattr(
        settings, 'GITLAB_USER_INFO_URL', 'https://gitlab.com/api/v3/user'
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
