from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import DoubanProvider


urlpatterns = default_urlpatterns(DoubanProvider)
