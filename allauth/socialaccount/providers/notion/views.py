from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .client import NotionOAuth2Client
from .provider import NotionProvider


class NotionOAuth2Adapter(OAuth2Adapter):
    provider_id = NotionProvider.id
    basic_auth = True
    client_class = NotionOAuth2Client

    authorize_url = "https://api.notion.com/v1/oauth/authorize"
    access_token_url = "https://api.notion.com/v1/oauth/token"

    def complete_login(self, request, app, token, **kwargs):
        return self.get_provider().sociallogin_from_response(
            request, kwargs["response"]
        )


oauth2_login = OAuth2LoginView.adapter_view(NotionOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(NotionOAuth2Adapter)
