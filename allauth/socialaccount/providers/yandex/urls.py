from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.yandex.provider import YandexProvider


urlpatterns = default_urlpatterns(YandexProvider)
