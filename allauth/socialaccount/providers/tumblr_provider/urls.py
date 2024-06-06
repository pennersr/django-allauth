from allauth.socialaccount.providers.oauth_provider.urls import default_urlpatterns

from .provider import TumblrProvider


urlpatterns = default_urlpatterns(TumblrProvider)
