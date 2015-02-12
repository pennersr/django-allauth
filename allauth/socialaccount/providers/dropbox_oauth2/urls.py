from allauth.socialaccount.providers.oauth.urls import default_urlpatterns

from .provider import DropboxOAuth2Provider

urlpatterns = default_urlpatterns(DropboxOAuth2Provider)
