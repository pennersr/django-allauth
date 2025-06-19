from allauth.socialaccount.providers.hubspot.provider import HubspotProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(HubspotProvider)
