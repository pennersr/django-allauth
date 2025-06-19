from allauth.socialaccount.providers.dingtalk.provider import DingTalkProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(DingTalkProvider)
