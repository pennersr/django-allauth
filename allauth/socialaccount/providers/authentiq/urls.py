from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import AuthentiqProvider


urlpatterns = default_urlpatterns(AuthentiqProvider)
