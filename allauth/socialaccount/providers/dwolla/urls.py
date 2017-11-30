from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import DwollaProvider


urlpatterns = default_urlpatterns(DwollaProvider)
