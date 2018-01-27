from __future__ import unicode_literals

import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import MicrosoftGraphProvider


class MicrosoftGraphOAuth2Adapter(OAuth2Adapter):
    provider_id = MicrosoftGraphProvider.id

    def __init__(self, request):
        super(MicrosoftGraphOAuth2Adapter, self).__init__(request)
        provider = self.get_provider()
        tenant = provider.get_settings().get('tenant') or 'common'
        base_url = 'https://login.microsoftonline.com/{0}'.format(tenant)
        self.access_token_url = '{0}/oauth2/v2.0/token'.format(base_url)
        self.authorize_url = '{0}/oauth2/v2.0/authorize'.format(base_url)
        self.profile_url = 'https://graph.microsoft.com/v1.0/me/'

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': 'Bearer {0}'.format(token.token)}
        resp = requests.get(self.profile_url, headers=headers)
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth2_login = OAuth2LoginView.adapter_view(MicrosoftGraphOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(MicrosoftGraphOAuth2Adapter)
