from allauth.socialaccount.providers.oauth.urls import default_urlpatterns

from .provider import FlickrProvider


urlpatterns = default_urlpatterns(FlickrProvider)
