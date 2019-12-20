import requests

from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import EdxProvider


class EdxOAuth2Adapter(OAuth2Adapter):
    provider_id = EdxProvider.id
    provider_default_url = 'https://edx.org'

    settings = app_settings.PROVIDERS.get(provider_id, {})
    provider_base_url = settings.get('EDX_URL', provider_default_url)

    access_token_url = '{0}/oauth2/access_token'.format(provider_base_url)
    authorize_url = '{0}/oauth2/authorize/'.format(provider_base_url)
    profile_url = '{0}/api/user/v1/me'.format(provider_base_url)
    account_url = '{0}/api/user/v1/accounts/{1}'
    supports_state = False
    redirect_uri_protocol = 'https'

    def complete_login(self, request, app, token, **kwargs):
        response = requests.get(
            self.profile_url,
            params={'access_token': token})
        extra_data = response.json()

        if extra_data.get('email', None) is None:
            response = requests.get(
                self.account_url.format(self.provider_base_url,
                                        extra_data['username']),
                params={'access_token': token})
            extra_data = response.json()

        return self.get_provider().sociallogin_from_response(
            request,
            extra_data)


oauth2_login = OAuth2LoginView.adapter_view(EdxOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(EdxOAuth2Adapter)
