from allauth.socialaccount.providers.openid_connect.urls import default_urlpatterns

from .provider import QQProvider

urlpatterns = default_urlpatterns(QQProvider)

