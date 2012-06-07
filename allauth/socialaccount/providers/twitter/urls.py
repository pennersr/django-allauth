from allauth.socialaccount.providers.oauth.urls import default_urlpatterns
from models import TwitterProvider

urlpatterns = default_urlpatterns(TwitterProvider)
