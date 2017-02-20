from allauth.socialaccount.providers.oauth.urls import default_urlpatterns

from .provider import TwitterProvider


urlpatterns = default_urlpatterns(TwitterProvider)
