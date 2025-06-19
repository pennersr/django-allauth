from allauth.socialaccount.providers.douban.provider import DoubanProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(DoubanProvider)
