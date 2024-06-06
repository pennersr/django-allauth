from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import WeiboProvider


urlpatterns = default_urlpatterns(WeiboProvider)
