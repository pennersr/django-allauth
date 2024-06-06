from allauth.socialaccount.providers.globus_provider.provider import GlobusProvider
from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns


urlpatterns = default_urlpatterns(GlobusProvider)
