"""URLs for Patreon Provider"""

from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import PatreonProvider


urlpatterns = default_urlpatterns(PatreonProvider)
