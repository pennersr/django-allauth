from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.reddit.provider import RedditProvider


urlpatterns = default_urlpatterns(RedditProvider)
