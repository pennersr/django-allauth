from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.stocktwits.provider import StocktwitsProvider


urlpatterns = default_urlpatterns(StocktwitsProvider)
