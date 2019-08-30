from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import NextCloudProvider


urlpatterns = default_urlpatterns(NextCloudProvider)
