from allauth.socialaccount.providers.feedly.provider import FeedlyProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(FeedlyProvider)
