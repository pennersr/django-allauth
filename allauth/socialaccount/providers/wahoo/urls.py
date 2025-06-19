from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.wahoo.provider import WahooProvider


urlpatterns = default_urlpatterns(WahooProvider)
