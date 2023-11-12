from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import DingTalkProvider


urlpatterns = default_urlpatterns(DingTalkProvider)
