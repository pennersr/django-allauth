from allauth.socialaccount.providers.coinbase.provider import CoinbaseProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(CoinbaseProvider)
