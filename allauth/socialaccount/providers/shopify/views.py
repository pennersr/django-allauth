import re

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest

from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class ShopifyOAuth2Adapter(OAuth2Adapter):
    provider_id = "shopify"
    scope_delimiter = ","

    def _shop_domain(self):
        shop = self.request.GET.get("shop", "")
        if "." not in shop:
            shop = "{}.myshopify.com".format(shop)
        # Ensure the provided hostname parameter is a valid hostname,
        # ends with myshopify.com, and does not contain characters
        # other than letters (a-z), numbers (0-9), dots, and hyphens.
        if not re.match(r"^[a-z0-9-]+\.myshopify\.com$", shop):
            raise ImmediateHttpResponse(
                HttpResponseBadRequest("Invalid `shop` parameter")
            )
        return shop

    def _shop_url(self, path):
        shop = self._shop_domain()
        return "https://{}{}".format(shop, path)

    @property
    def access_token_url(self):
        return self._shop_url("/admin/oauth/access_token")

    @property
    def authorize_url(self):
        return self._shop_url("/admin/oauth/authorize")

    @property
    def profile_url(self):
        return self._shop_url("/admin/shop.json")

    def complete_login(self, request, app, token, **kwargs):
        headers = {"X-Shopify-Access-Token": "{token}".format(token=token.token)}
        response = (
            get_adapter().get_requests_session().get(self.profile_url, headers=headers)
        )
        extra_data = response.json()
        associated_user = kwargs["response"].get("associated_user")
        if associated_user:
            extra_data["associated_user"] = associated_user
        return self.get_provider().sociallogin_from_response(request, extra_data)


class ShopifyOAuth2LoginView(OAuth2LoginView):
    def dispatch(self, request, *args, **kwargs):
        is_embedded = (
            getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
            .get("shopify", {})
            .get("IS_EMBEDDED", False)
        )
        if is_embedded:
            # TODO: This bypasses LOGIN_ON_GET, but:
            #
            #     The Embedded App SDK (EASDK) and backwards compatibility layer
            #     are being removed from Shopify on January 1, 2022.
            #
            # So this needs to be dropped/revisitted anyway.
            response = super().login(request, *args, **kwargs)
            """
            Shopify embedded apps (that run within an iFrame) require a JS
            (not server) redirect for starting the oauth2 process.

            See Also:
            https://help.shopify.com/api/sdks/embedded-app-sdk/getting-started#oauth
            """
            js = "".join(
                (
                    "<!DOCTYPE html><html><head>" '<script type="text/javascript">',
                    'window.top.location.href = "{url}";'.format(url=response.url),
                    "</script></head><body></body></html>",
                )
            )
            response = HttpResponse(content=js)
            # Because this view will be within shopify's iframe
            response.xframe_options_exempt = True
            return response
        return super().dispatch(request, *args, **kwargs)


oauth2_login = ShopifyOAuth2LoginView.adapter_view(ShopifyOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(ShopifyOAuth2Adapter)
