from django.contrib.auth.models import User

from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)
from allauth.socialaccount import requests

from allauth.socialaccount.models import SocialAccount, SocialLogin

from provider import GitHubProvider

class GitHubOAuth2Adapter(OAuth2Adapter):
    provider_id = GitHubProvider.id
    access_token_url = 'https://github.com/login/oauth/access_token'
    authorize_url = 'https://github.com/login/oauth/authorize'
    profile_url = 'https://api.github.com/user'

    def complete_login(self, request, app, token):
        resp = requests.get(self.profile_url,
                            params={ 'access_token': token.token })
        extra_data = resp.json
        uid = str(extra_data['id'])
        user = User(username=extra_data.get('login', ''),
                    email=extra_data.get('email', ''),
                    first_name=extra_data.get('name', ''))
        account = SocialAccount(user=user,
                                uid=uid,
                                extra_data=extra_data,
                                provider=self.provider_id)
        return SocialLogin(account)


oauth2_login = OAuth2LoginView.adapter_view(GitHubOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(GitHubOAuth2Adapter)

