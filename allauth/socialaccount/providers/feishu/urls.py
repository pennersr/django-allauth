from allauth.socialaccount.providers.feishu.provider import FeishuProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(FeishuProvider)
