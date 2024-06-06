from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import YahooProvider


urlpatterns = default_urlpatterns(YahooProvider)
