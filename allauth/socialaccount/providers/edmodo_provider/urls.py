from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import EdmodoProvider


urlpatterns = default_urlpatterns(EdmodoProvider)
