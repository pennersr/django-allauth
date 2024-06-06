from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import BaiduProvider


urlpatterns = default_urlpatterns(BaiduProvider)
