from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import AngelListProvider


urlpatterns = default_urlpatterns(AngelListProvider)
