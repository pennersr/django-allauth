from allauth.socialaccount.providers.oauth.urls import default_urlpatterns

from .provider import EvernoteProvider

urlpatterns = default_urlpatterns(EvernoteProvider)

