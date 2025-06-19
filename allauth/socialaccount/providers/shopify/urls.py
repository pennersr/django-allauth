from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.shopify.provider import ShopifyProvider


urlpatterns = default_urlpatterns(ShopifyProvider)
