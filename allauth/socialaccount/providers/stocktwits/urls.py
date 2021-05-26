from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import StocktwitsProvider


urlpatterns = default_urlpatterns(StocktwitsProvider)
