from __future__ import unicode_literals

import requests
from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)
from .provider import MSLiveProvider


class MSLiveOAuth2Adapter(OAuth2Adapter):
    provider_id = MSLiveProvider.id
    access_token_url = 'https://login.live.com/oauth20_token.srf'
    authorize_url = 'https://login.live.com/oauth20_authorize.srf'
    profile_url = 'https://apis.live.net/v5.0/me'

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': 'Bearer {0}'.format(token.token)}
        resp = requests.get(self.profile_url, headers=headers)

#example of whats returned (in python format):
#{u'first_name': u'James', u'last_name': u'Smith', u'name': u'James Smith', u'locale': u'en_US', u'gender': None, 
# u'emails': {u'personal': None, u'account': u'jsmith@xyz.net', u'business': None, u'preferred': u'jsmith@xyz.net'}, 
# u'link': u'https://profile.live.com/', u'updated_time': u'2014-02-07T00:35:27+0000',
# u'id': u'83605e110af6ff98'}

        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth2_login = OAuth2LoginView.adapter_view(MSLiveOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(MSLiveOAuth2Adapter)

