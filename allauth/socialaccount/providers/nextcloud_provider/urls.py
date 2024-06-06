from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import NextCloudProvider


urlpatterns = default_urlpatterns(NextCloudProvider)
