import requests

from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)

from .provider import SalesforceProvider


class SalesforceOAuth2Adapter(OAuth2Adapter):
    provider_id = SalesforceProvider.id
    access_token_url = 'https://login.salesforce.com/services/oauth2/token'
    authorize_url = 'https://login.salesforce.com/services/oauth2/authorize'
    profile_url = 'https://login.salesforce.com/services/oauth2/userinfo'

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.profile_url,
                            params={'access_token': token.token,
                                    'format': 'json'})
        resp.raise_for_status()
        extra_data = resp.json()
        login = self.get_provider() \
            .sociallogin_from_response(request,
                                       extra_data)
        return login


oauth2_login = OAuth2LoginView.adapter_view(SalesforceOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(SalesforceOAuth2Adapter)
