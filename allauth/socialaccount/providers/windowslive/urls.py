from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.windowslive.provider import WindowsLiveProvider


urlpatterns = default_urlpatterns(WindowsLiveProvider)
