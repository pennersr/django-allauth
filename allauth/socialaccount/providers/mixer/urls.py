from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import MixerProvider


urlpatterns = default_urlpatterns(MixerProvider)
