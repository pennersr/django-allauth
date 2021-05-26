from allauth.socialaccount.providers.globus.provider import GlobusProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(GlobusProvider)
