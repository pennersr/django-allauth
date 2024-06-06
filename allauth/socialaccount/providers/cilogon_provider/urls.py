from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import CILogonProvider


urlpatterns = default_urlpatterns(CILogonProvider)
