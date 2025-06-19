from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.weixin.provider import WeixinProvider


urlpatterns = default_urlpatterns(WeixinProvider)
