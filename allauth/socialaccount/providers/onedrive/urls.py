from allauth.socialaccount.providers.oauth.urls import default_urlpatterns

from .provider import OnedriveOAuth2Provider


urlpatterns = default_urlpatterns(OnedriveOAuth2Provider)
