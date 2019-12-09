from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import EdxProvider


urlpatterns = default_urlpatterns(EdxProvider)
