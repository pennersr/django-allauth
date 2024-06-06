from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import StravaProvider


urlpatterns = default_urlpatterns(StravaProvider)
