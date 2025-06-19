from allauth.socialaccount.providers.baidu.provider import BaiduProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(BaiduProvider)
