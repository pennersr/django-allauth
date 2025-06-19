from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.snapchat.provider import SnapchatProvider


urlpatterns = default_urlpatterns(SnapchatProvider)
