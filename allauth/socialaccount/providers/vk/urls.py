from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.vk.provider import VKProvider


urlpatterns = default_urlpatterns(VKProvider)
