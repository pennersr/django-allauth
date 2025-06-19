from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.quickbooks.provider import QuickBooksOAuth2Provider


urlpatterns = default_urlpatterns(QuickBooksOAuth2Provider)
