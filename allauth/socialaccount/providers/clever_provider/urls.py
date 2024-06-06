from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import CleverProvider


urlpatterns = default_urlpatterns(CleverProvider)
