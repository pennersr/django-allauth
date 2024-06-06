from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import QuestradeProvider


urlpatterns = default_urlpatterns(QuestradeProvider)
