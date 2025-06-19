from allauth.socialaccount.providers.oauth.urls import default_urlpatterns
from allauth.socialaccount.providers.xing.provider import XingProvider


urlpatterns = default_urlpatterns(XingProvider)
