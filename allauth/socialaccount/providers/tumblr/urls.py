from allauth.socialaccount.providers.oauth.urls import default_urlpatterns

from .provider import TumblrProvider


urlpatterns = default_urlpatterns(TumblrProvider)
