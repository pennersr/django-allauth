from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import BitlyProvider


urlpatterns = default_urlpatterns(BitlyProvider)
