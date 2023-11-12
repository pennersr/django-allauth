from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import CleverProvider


urlpatterns = default_urlpatterns(CleverProvider)
