from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import QuickbooksOAuth2Provider


urlpatterns = default_urlpatterns(QuickbooksOAuth2Provider)