from allauth.socialaccount.providers.openid_connect.urls import default_urlpatterns

from .provider import CernProvider


urlpatterns = default_urlpatterns(CernProvider)
