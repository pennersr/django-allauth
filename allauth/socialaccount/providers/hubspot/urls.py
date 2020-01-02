from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import HubSpotProvider


urlpatterns = default_urlpatterns(HubSpotProvider)
