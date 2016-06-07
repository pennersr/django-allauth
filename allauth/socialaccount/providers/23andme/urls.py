from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from .provider import TwentyTreeAndMeProvider

urlpatterns = default_urlpatterns(TwentyTreeAndMeProvider)
