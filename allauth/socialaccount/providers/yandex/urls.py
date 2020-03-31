from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import YandexProvider


urlpatterns = default_urlpatterns(YandexProvider)
