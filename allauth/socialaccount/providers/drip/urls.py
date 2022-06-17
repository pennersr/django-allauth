from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import DripProvider


urlpatterns = default_urlpatterns(DripProvider)
