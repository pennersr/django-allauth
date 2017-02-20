from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import BaiduProvider


urlpatterns = default_urlpatterns(BaiduProvider)
