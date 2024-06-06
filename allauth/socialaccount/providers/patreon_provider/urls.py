"""URLs for Patreon Provider"""

from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import PatreonProvider


urlpatterns = default_urlpatterns(PatreonProvider)
