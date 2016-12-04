from allauth.socialaccount.providers.oauth.urls import default_urlpatterns
from .provider import FiveHundredPxProvider

urlpatterns = default_urlpatterns(FiveHundredPxProvider)
