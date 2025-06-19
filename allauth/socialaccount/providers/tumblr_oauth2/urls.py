from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.tumblr_oauth2.provider import TumblrOAuth2Provider


urlpatterns = default_urlpatterns(TumblrOAuth2Provider)
