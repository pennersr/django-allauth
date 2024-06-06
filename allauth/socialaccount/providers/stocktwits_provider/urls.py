from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import StocktwitsProvider


urlpatterns = default_urlpatterns(StocktwitsProvider)
