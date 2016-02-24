import requests
from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)

from .provider import RobinhoodProvider


class RobinhoodOAuth2Adapter(OAuth2Adapter):
    provider_id = RobinhoodProvider.id

    @property
    def authorize_url(self):
        return 'https://www.robinhood.com/oauth2/authorize/'

    @property
    def access_token_url(self):
        return 'https://api.robinhood.com/oauth2/token/'

    @property
    def profile_url(self):
        return 'https://api.robinhood.com/user/id/'

    def complete_login(self, request, app, token, **kwargs):
        response = requests.get(self.profile_url,
                                headers={'Authorization': 'Bearer %s' % token.token})
        extra_data = response.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(RobinhoodOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(RobinhoodOAuth2Adapter)
