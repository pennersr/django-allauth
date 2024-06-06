from allauth.socialaccount.providers.notion_provider.provider import NotionProvider
from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns


urlpatterns = default_urlpatterns(NotionProvider)
