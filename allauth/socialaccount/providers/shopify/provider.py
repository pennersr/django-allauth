from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class ShopifyAccount(ProviderAccount):
    pass


class ShopifyProvider(OAuth2Provider):
    id = 'shopify'
    name = 'Shopify'
    account_class = ShopifyAccount

    def get_auth_params(self, request, action):
        ret = super(ShopifyProvider, self).get_auth_params(request, action)
        shop = request.GET.get('shop', None)
        if shop:
            ret.update({'shop': shop})
        return ret

    def get_default_scope(self):
        return ['read_orders', 'read_products']

    def extract_uid(self, data):
        return str(data['shop']['id'])

    def extract_common_fields(self, data):
        # See: https://docs.shopify.com/api/shop
        # User is only available with Shopify Plus, email is the only
        # common field
        return dict(email=data['shop']['email'])


providers.registry.register(ShopifyProvider)
