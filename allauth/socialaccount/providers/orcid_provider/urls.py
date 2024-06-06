from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import OrcidProvider


urlpatterns = default_urlpatterns(OrcidProvider)
