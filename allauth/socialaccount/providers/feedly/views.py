from __future__ import unicode_literals

import requests
from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)
from .provider import FeedlyProvider


class FeedlyOAuth2Adapter(OAuth2Adapter):
    provider_id = FeedlyProvider.id
    access_token_url = 'https://%s/v3/auth/token' % settings.get('FEEDLY_HOST', 'cloud.feedly.com')
    authorize_url = 'https://%s/v3/auth/auth' % settings.get('FEEDLY_HOST', 'cloud.feedly.com')
    profile_url = 'https://%s/v3/profile' % settings.get('FEEDLY_HOST', 'cloud.feedly.com')


    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': 'OAuth {0}'.format(token.token)}
        resp = requests.get(self.profile_url, headers=headers)
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth2_login = OAuth2LoginView.adapter_view(FeedlyOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(FeedlyOAuth2Adapter)
