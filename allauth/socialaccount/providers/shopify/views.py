from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)
import requests
from .provider import ShopifyProvider


class ShopifyOAuth2Client(OAuth2Client):
    def get_redirect_url(self, request, extra_params):
        self.shop = extra_params['shop']
        _url = 'https://{}.{}'.format(
            self.shop,
            super(ShopifyOAuth2Client, self).get_redirect_url(request, extra_params))
        return _url


class ShopifyOAuth2LoginView(OAuth2LoginView):
    def get_client(self, request, app):
        client = super(ShopifyOAuth2LoginView, self).get_client(request, app)
        client.__class__ = ShopifyOAuth2Client
        return client


class ShopifyOAuth2CallbackView(OAuth2CallbackView):
    def get_client(self, request, app):
        client = super(ShopifyOAuth2CallbackView, self).get_client(request, app)
        client.access_token_url = 'https://{}/{}'.format(
            request.GET.get('shop'), client.access_token_url)
        return client


class ShopifyOAuth2Adapter(OAuth2Adapter):
    provider_id = ShopifyProvider.id
    supports_state = False
    endpoint = 'myshopify.com/admin'
    access_token_url = 'admin/oauth/access_token'

    @property
    def authorize_url(self):
        return '{}/oauth/authorize'.format(self.endpoint)

    @property
    def profile_url(self):
        return 'admin/shop.json'

    def complete_login(self, request, app, token, **kwargs):
        headers = {'X-Shopify-Access-Token': '{token}'.format(token=token.token)}
        response = requests.get('https://{}/{}'.format(request.GET['shop'], self.profile_url),
                                headers=headers)
        extra_data = response.json()
        # save access token with extra data, to be able to use it in social_account_removed
        extra_data.update({'token': token.token})
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = ShopifyOAuth2LoginView.adapter_view(ShopifyOAuth2Adapter)
oauth2_callback = ShopifyOAuth2CallbackView.adapter_view(ShopifyOAuth2Adapter)
