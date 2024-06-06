from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import QuickBooksOAuth2Provider


urlpatterns = default_urlpatterns(QuickBooksOAuth2Provider)
