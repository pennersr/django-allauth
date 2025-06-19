from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.soundcloud.provider import SoundCloudProvider


urlpatterns = default_urlpatterns(SoundCloudProvider)
