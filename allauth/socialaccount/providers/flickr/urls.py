from allauth.socialaccount.providers.flickr.provider import FlickrProvider
from allauth.socialaccount.providers.oauth.urls import default_urlpatterns


urlpatterns = default_urlpatterns(FlickrProvider)
