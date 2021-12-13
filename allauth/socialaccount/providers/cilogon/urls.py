from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import CILogonProvider


urlpatterns = default_urlpatterns(CILogonProvider)
