from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import TwentyThreeAndMeProvider


urlpatterns = default_urlpatterns(TwentyThreeAndMeProvider)
