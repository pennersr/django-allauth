from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import TumblrOAuth2Provider


urlpatterns = default_urlpatterns(TumblrOAuth2Provider)
