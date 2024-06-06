from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import WeixinProvider


urlpatterns = default_urlpatterns(WeixinProvider)
