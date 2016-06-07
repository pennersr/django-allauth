from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from .provider import TwentyThreeAndMeProvider

urlpatterns = default_urlpatterns(TwentyThreeAndMeProvider)
