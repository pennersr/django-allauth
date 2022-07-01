from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import DingtalkProvider


urlpatterns = default_urlpatterns(DingtalkProvider)
