from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.twentythreeandme.provider import (
    TwentyThreeAndMeProvider,
)


urlpatterns = default_urlpatterns(TwentyThreeAndMeProvider)
