from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import AtlassianProvider


urlpatterns = default_urlpatterns(AtlassianProvider)
