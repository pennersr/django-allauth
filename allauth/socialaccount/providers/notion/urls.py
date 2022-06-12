from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import NotionProvider


urlpatterns = default_urlpatterns(NotionProvider)
