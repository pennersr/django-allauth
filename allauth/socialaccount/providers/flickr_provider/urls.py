from allauth.socialaccount.providers.oauth_provider.urls import default_urlpatterns

from .provider import FlickrProvider


urlpatterns = default_urlpatterns(FlickrProvider)
