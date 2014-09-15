from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from .provider import CoinbaseProvider

urlpatterns = default_urlpatterns(CoinbaseProvider)
