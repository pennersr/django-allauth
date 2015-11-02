from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from .provider import ShopifyProvider

urlpatterns = default_urlpatterns(ShopifyProvider)
