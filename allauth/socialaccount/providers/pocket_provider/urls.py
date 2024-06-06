from allauth.socialaccount.providers.oauth_provider.urls import default_urlpatterns

from .provider import PocketProvider


urlpatterns = default_urlpatterns(PocketProvider)
