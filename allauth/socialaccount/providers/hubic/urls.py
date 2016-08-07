from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import HubicProvider

urlpatterns = default_urlpatterns(HubicProvider)
