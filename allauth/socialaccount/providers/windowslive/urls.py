from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import WindowsLiveProvider


urlpatterns = default_urlpatterns(WindowsLiveProvider)
