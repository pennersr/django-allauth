from allauth.socialaccount.providers.oauth.urls import default_urlpatterns
from .provider import VimeoProvider

urlpatterns = default_urlpatterns(VimeoProvider)
