from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import YahooProvider


urlpatterns = default_urlpatterns(YahooProvider)
