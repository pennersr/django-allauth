from django.conf import settings

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class ShopifyAccount(ProviderAccount):
    pass


class ShopifyProvider(OAuth2Provider):
    id = "shopify"
    name = "Shopify"
    account_class = ShopifyAccount

    @property
    def is_per_user(self):
        grant_options = (
            getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
            .get("shopify", {})
            .get("AUTH_PARAMS", {})
            .get("grant_options[]", "")
        )
        return grant_options.lower().strip() == "per-user"

    def get_auth_params(self, request, action):
        ret = super(ShopifyProvider, self).get_auth_params(request, action)
        shop = request.GET.get("shop", None)
        if shop:
            ret.update({"shop": shop})
        return ret

    def get_default_scope(self):
        return ["read_orders", "read_products"]

    def extract_uid(self, data):
        if self.is_per_user:
            return str(data["associated_user"]["id"])
        else:
            return str(data["shop"]["id"])

    def extract_common_fields(self, data):
        if self.is_per_user:
            return dict(
                email=data["associated_user"]["email"],
                first_name=data["associated_user"]["first_name"],
                last_name=data["associated_user"]["last_name"],
            )
        else:
            # See: https://docs.shopify.com/api/shop
            # Without online mode, User is only available with Shopify Plus,
            # email is the only common field
            return dict(email=data["shop"]["email"])


provider_classes = [ShopifyProvider]
