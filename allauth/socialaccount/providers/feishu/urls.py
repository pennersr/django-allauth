from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import FeishuProvider


urlpatterns = default_urlpatterns(FeishuProvider)
