from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import UNiDAYSProvider


urlpatterns = default_urlpatterns(UNiDAYSProvider)
