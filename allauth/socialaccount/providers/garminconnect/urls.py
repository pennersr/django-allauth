from allauth.socialaccount.providers.oauth.urls import default_urlpatterns

from .provider import GarminConnectProvider


urlpatterns = default_urlpatterns(GarminConnectProvider)
