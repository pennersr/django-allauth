from allauth.socialaccount.providers.doximity.provider import DoximityProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(DoximityProvider)
