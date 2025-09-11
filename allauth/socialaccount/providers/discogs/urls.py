from allauth.socialaccount.providers.discogs.provider import DiscogsProvider
from allauth.socialaccount.providers.oauth.urls import default_urlpatterns


urlpatterns = default_urlpatterns(DiscogsProvider)
