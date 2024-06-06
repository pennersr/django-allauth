from allauth.socialaccount.providers.oauth_provider.urls import default_urlpatterns

from .provider import FiveHundredPxProvider


urlpatterns = default_urlpatterns(FiveHundredPxProvider)
