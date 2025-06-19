from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.zoom.provider import ZoomProvider


urlpatterns = default_urlpatterns(ZoomProvider)
