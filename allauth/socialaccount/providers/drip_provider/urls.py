from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import DripProvider


urlpatterns = default_urlpatterns(DripProvider)
