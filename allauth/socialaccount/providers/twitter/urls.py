from allauth.socialaccount.providers.oauth.urls import default_urlpatterns
from allauth.socialaccount.providers.twitter.provider import TwitterProvider


urlpatterns = default_urlpatterns(TwitterProvider)
