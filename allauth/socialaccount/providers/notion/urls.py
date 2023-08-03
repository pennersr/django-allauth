from allauth.socialaccount.providers.notion.provider import NotionProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(NotionProvider)
