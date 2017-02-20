from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import SoundCloudProvider


urlpatterns = default_urlpatterns(SoundCloudProvider)
