from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import CoinbaseProvider


urlpatterns = default_urlpatterns(CoinbaseProvider)
