from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import ZoomProvider


urlpatterns = default_urlpatterns(ZoomProvider)
