from allauth.socialaccount.providers.oauth.urls import default_urlpatterns
from allauth.socialaccount.providers.tumblr.provider import TumblrProvider


urlpatterns = default_urlpatterns(TumblrProvider)
