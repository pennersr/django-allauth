from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import DoximityProvider


urlpatterns = default_urlpatterns(DoximityProvider)
