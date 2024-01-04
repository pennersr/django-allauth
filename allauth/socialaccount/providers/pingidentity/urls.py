from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import PingIdentityProvider


urlpatterns = default_urlpatterns(PingIdentityProvider)
