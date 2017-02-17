from allauth.socialaccount.providers.oauth.urls import default_urlpatterns

from .provider import DropboxProvider


urlpatterns = default_urlpatterns(DropboxProvider)
