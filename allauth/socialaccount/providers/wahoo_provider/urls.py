from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import WahooProvider


urlpatterns = default_urlpatterns(WahooProvider)
