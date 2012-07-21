from allauth.socialaccount.providers.oauth.urls import default_urlpatterns
from provider import SoundCloudProvider 

urlpatterns = default_urlpatterns(SoundCloudProvider)
