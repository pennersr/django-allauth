from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import CanvasProvider


urlpatterns = default_urlpatterns(CanvasProvider)
