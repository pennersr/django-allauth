from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import EdxProvider


urlpatterns = default_urlpatterns(EdxProvider)
