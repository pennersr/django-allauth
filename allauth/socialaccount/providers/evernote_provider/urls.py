from allauth.socialaccount.providers.oauth_provider.urls import default_urlpatterns

from .provider import EvernoteProvider


urlpatterns = default_urlpatterns(EvernoteProvider)
