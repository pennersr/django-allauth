from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import QuestradeProvider


urlpatterns = default_urlpatterns(QuestradeProvider)
