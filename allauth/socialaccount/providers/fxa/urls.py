from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import FirefoxAccountsProvider


urlpatterns = default_urlpatterns(FirefoxAccountsProvider)
