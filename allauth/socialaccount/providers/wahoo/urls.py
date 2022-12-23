from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import WahooProvider


urlpatterns = default_urlpatterns(WahooProvider)
