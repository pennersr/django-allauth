from allauth.socialaccount.providers.dropbox.provider import DropboxOAuth2Provider
from allauth.socialaccount.providers.oauth.urls import default_urlpatterns


urlpatterns = default_urlpatterns(DropboxOAuth2Provider)
