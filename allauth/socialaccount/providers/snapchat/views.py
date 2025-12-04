from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)
from allauth.socialaccount.providers.snapchat.constants import PROVIDER_ID, Scope


class SnapchatOAuth2Adapter(OAuth2Adapter):
    provider_id = PROVIDER_ID

    access_token_url = "https://accounts.snapchat.com/accounts/oauth2/token"  # nosec
    authorize_url = "https://accounts.snapchat.com/accounts/oauth2/auth"
    identity_url = "https://api.snapkit.com/v1/me"

    def complete_login(self, request, app, token, **kwargs):
        extra_data = self.get_data(token.token)
        return self.get_provider().sociallogin_from_response(request, extra_data)

    def get_data(self, token):
        settings = app_settings.PROVIDERS.get(self.provider_id, {})
        provider_scope = settings.get(
            "SCOPE",
            "['https://auth.snapchat.com/oauth2/api/user.external_id', 'https://auth.snapchat.com/oauth2/api/user.display_name']",
        )

        hed = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json;charset=UTF-8",
        }
        if Scope.BITMOJI in provider_scope:
            data = {"query": "{ me { externalId displayName bitmoji { avatar id } } }"}
        else:
            data = {"query": "{ me { externalId displayName } }"}

        with get_adapter().get_requests_session() as sess:
            resp = sess.post(self.identity_url, headers=hed, json=data)
            resp.raise_for_status()
            data = resp.json()

        if not data.get("data"):
            raise OAuth2Error()

        return data


oauth2_login = OAuth2LoginView.adapter_view(SnapchatOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(SnapchatOAuth2Adapter)
