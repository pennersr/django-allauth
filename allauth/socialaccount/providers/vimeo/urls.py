from allauth.socialaccount.providers.oauth.urls import default_urlpatterns
from allauth.socialaccount.providers.vimeo.provider import VimeoProvider


urlpatterns = default_urlpatterns(VimeoProvider)
