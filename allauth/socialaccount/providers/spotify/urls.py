from allauth.socialaccount.providers.oauth.urls import default_urlpatterns
from allauth.socialaccount.providers.spotify.provider import SpotifyOAuth2Provider


urlpatterns = default_urlpatterns(SpotifyOAuth2Provider)
