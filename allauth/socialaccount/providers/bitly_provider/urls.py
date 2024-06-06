from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import BitlyProvider


urlpatterns = default_urlpatterns(BitlyProvider)
