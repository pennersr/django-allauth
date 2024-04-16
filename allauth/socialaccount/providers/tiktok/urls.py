from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import TiktokProvider


urlpatterns = default_urlpatterns(TiktokProvider)
