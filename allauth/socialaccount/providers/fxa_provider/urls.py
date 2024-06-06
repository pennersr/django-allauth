from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import FirefoxAccountsProvider


urlpatterns = default_urlpatterns(FirefoxAccountsProvider)
