from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import DAuthProvider


urlpatterns = default_urlpatterns(DAuthProvider)
