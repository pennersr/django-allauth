from allauth.socialaccount.providers.oauth_provider.urls import default_urlpatterns

from .provider import XingProvider


urlpatterns = default_urlpatterns(XingProvider)
