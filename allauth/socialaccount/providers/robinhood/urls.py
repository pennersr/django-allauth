from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from .provider import RobinhoodProvider

urlpatterns = default_urlpatterns(RobinhoodProvider)
