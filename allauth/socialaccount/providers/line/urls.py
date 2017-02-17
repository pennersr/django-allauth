from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import LineProvider


urlpatterns = default_urlpatterns(LineProvider)
