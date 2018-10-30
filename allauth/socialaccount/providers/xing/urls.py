from allauth.socialaccount.providers.oauth.urls import default_urlpatterns

from .provider import XingProvider


urlpatterns = default_urlpatterns(XingProvider)
