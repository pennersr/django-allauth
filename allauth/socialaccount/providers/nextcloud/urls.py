from allauth.socialaccount.providers.nextcloud.provider import NextCloudProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(NextCloudProvider)
