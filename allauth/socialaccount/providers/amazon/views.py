import logging

import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import AmazonProvider

log = logging.getLogger(__name__)

class AmazonOAuth2Adapter(OAuth2Adapter):
    provider_id = AmazonProvider.id
    access_token_url = 'https://api.amazon.com/auth/o2/token'
    authorize_url = 'http://www.amazon.com/ap/oa'
    profile_url = 'https://www.amazon.com/ap/user/profile'
    supports_state = False
    redirect_uri_protocol = 'https'

    def complete_login(self, request, app, token, **kwargs):
        response = requests.get(
            self.profile_url,
            params={'access_token': token})
        log.debug(
            f'{self.__class__.__name__}. complete_login '
            f'user_id -> {request.user.id} '
            f'status code -> {response.status_code} '
            f'response text -> {response.text}'
        )
        extra_data = response.json()
        if 'Profile' in extra_data:
            extra_data = {
                'user_id': extra_data['Profile']['CustomerId'],
                'name': extra_data['Profile']['Name'],
                'email': extra_data['Profile']['PrimaryEmail']
            }
        return self.get_provider().sociallogin_from_response(
            request,
            extra_data)


oauth2_login = OAuth2LoginView.adapter_view(AmazonOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(AmazonOAuth2Adapter)
