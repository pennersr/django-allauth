from allauth.socialaccount.providers.hubic.provider import HubicProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(HubicProvider)
