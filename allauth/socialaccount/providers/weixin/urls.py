from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import WeixinProvider

urlpatterns = default_urlpatterns(WeixinProvider)
