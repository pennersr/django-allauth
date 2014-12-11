from __future__ import unicode_literals

import requests
from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)
from .provider import WindowsLiveProvider


class WindowsLiveOAuth2Adapter(OAuth2Adapter):
    provider_id = WindowsLiveProvider.id
    access_token_url = 'https://login.live.com/oauth20_token.srf'
    authorize_url = 'https://login.live.com/oauth20_authorize.srf'
    profile_url = 'https://apis.live.net/v5.0/me'

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': 'Bearer {0}'.format(token.token)}
        resp = requests.get(self.profile_url, headers=headers)

#example of whats returned (in python format):
#{'first_name': 'James', 'last_name': 'Smith',
# 'name': 'James Smith', 'locale': 'en_US', 'gender': None,
# 'emails': {'personal': None, 'account': 'jsmith@xyz.net',
# 'business': None, 'preferred': 'jsmith@xyz.net'},
# 'link': 'https://profile.live.com/',
# 'updated_time': '2014-02-07T00:35:27+0000',
# 'id': '83605e110af6ff98'}

        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth2_login = OAuth2LoginView.adapter_view(WindowsLiveOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(WindowsLiveOAuth2Adapter)
