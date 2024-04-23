from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import LichessProvider


urlpatterns = default_urlpatterns(LichessProvider)
