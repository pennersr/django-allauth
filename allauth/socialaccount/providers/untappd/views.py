import requests

from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)

from .client import UntappdOAuth2Client
from .provider import UntappdProvider


class UntappdOAuth2Adapter(OAuth2Adapter):
    provider_id = UntappdProvider.id
    access_token_url = 'https://untappd.com/oauth/authorize/'
    access_token_method = 'GET'
    authorize_url = 'https://untappd.com/oauth/authenticate/'
    user_info_url = 'https://api.untappd.com/v4/user/info/'
    supports_state = False

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.user_info_url,
                            params={'access_token': token.token})
        extra_data = resp.json()
        # TODO: get and store the email from the user info json
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


class UntappdOAuth2CallbackView(OAuth2CallbackView):
    """ Custom OAuth2CallbackView to return UntappdOAuth2Client """

    def get_client(self, request, app):
        client = super(UntappdOAuth2CallbackView, self).get_client(request,
                                                                   app)
        untappd_client = UntappdOAuth2Client(
            client.request, client.consumer_key, client.consumer_secret,
            client.access_token_method, client.access_token_url,
            client.callback_url, client.scope)
        return untappd_client

oauth2_login = OAuth2LoginView.adapter_view(UntappdOAuth2Adapter)
oauth2_callback = UntappdOAuth2CallbackView.adapter_view(UntappdOAuth2Adapter)
