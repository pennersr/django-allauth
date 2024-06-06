from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import HubicProvider


urlpatterns = default_urlpatterns(HubicProvider)
