import re
import requests

from django.http import HttpResponseBadRequest

from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)
from .provider import ShopifyProvider


class ShopifyOAuth2Adapter(OAuth2Adapter):
    provider_id = ShopifyProvider.id
    supports_state = False
    scope_delimiter = ','

    def _shop_domain(self):
        shop = self.request.GET.get('shop', '')
        if '.' not in shop:
            shop = '{}.myshopify.com'.format(shop)
        # Ensure the provided hostname parameter is a valid hostname,
        # ends with myshopify.com, and does not contain characters
        # other than letters (a-z), numbers (0-9), dots, and hyphens.
        if not re.match(r'^[a-z0-9-]+\.myshopify\.com$', shop):
            raise ImmediateHttpResponse(HttpResponseBadRequest(
                'Invalid `shop` parameter'))
        return shop

    def _shop_url(self, path):
        shop = self._shop_domain()
        return 'https://{}{}'.format(shop, path)

    @property
    def access_token_url(self):
        return self._shop_url('/admin/oauth/access_token')

    @property
    def authorize_url(self):
        return self._shop_url('/admin/oauth/authorize')

    @property
    def profile_url(self):
        return self._shop_url('/admin/shop.json')

    def complete_login(self, request, app, token, **kwargs):
        headers = {
            'X-Shopify-Access-Token': '{token}'.format(token=token.token)}
        response = requests.get(
            self.profile_url,
            headers=headers)
        extra_data = response.json()
        return self.get_provider().sociallogin_from_response(
            request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(ShopifyOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(ShopifyOAuth2Adapter)
