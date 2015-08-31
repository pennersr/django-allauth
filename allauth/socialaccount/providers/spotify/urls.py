from allauth.socialaccount.providers.oauth.urls import default_urlpatterns

from .provider import SpotifyOAuth2Provider

urlpatterns = default_urlpatterns(SpotifyOAuth2Provider)
