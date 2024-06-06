from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import DwollaProvider


urlpatterns = default_urlpatterns(DwollaProvider)
