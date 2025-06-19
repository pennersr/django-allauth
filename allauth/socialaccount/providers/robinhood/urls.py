from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.robinhood.provider import RobinhoodProvider


urlpatterns = default_urlpatterns(RobinhoodProvider)
