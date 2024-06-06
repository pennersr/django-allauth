from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import ShopifyProvider


urlpatterns = default_urlpatterns(ShopifyProvider)
