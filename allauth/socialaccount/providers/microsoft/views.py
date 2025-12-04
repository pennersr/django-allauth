import json

from allauth.core import context
from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


def _check_errors(response):
    try:
        data = response.json()
    except json.decoder.JSONDecodeError:
        raise OAuth2Error(f"Invalid JSON from Microsoft Graph API: {response.text}")

    if "id" not in data:
        error_message = "Error retrieving Microsoft profile"
        microsoft_error_message = data.get("error", {}).get("message")
        if microsoft_error_message:
            error_message = f"{error_message}: {microsoft_error_message}"
        raise OAuth2Error(error_message)

    return data


class MicrosoftGraphOAuth2Adapter(OAuth2Adapter):
    provider_id = "microsoft"

    def _build_tenant_url(self, path):
        settings = app_settings.PROVIDERS.get(self.provider_id, {})
        # Lower case "tenant" for backwards compatibility
        tenant = settings.get("TENANT", settings.get("tenant", "common"))
        # Prefer app based tenant setting.
        app = get_adapter().get_app(context.request, provider=self.provider_id)
        tenant = app.settings.get("tenant", tenant)
        login_url = app.settings.get("login_url", "https://login.microsoftonline.com")
        return f"{login_url}/{tenant}{path}"

    @property
    def access_token_url(self):
        return self._build_tenant_url("/oauth2/v2.0/token")

    @property
    def authorize_url(self):
        return self._build_tenant_url("/oauth2/v2.0/authorize")

    @property
    def profile_url(self):
        app = get_adapter().get_app(context.request, provider=self.provider_id)
        graph_url = app.settings.get("graph_url", "https://graph.microsoft.com")
        return f"{graph_url}/v1.0/me"

    user_properties = (
        "businessPhones",
        "displayName",
        "givenName",
        "id",
        "jobTitle",
        "mail",
        "mobilePhone",
        "officeLocation",
        "preferredLanguage",
        "surname",
        "userPrincipalName",
        "mailNickname",
        "companyName",
    )
    profile_url_params = {"$select": ",".join(user_properties)}

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": f"Bearer {token.token}"}
        with get_adapter().get_requests_session() as sess:
            response = sess.get(
                self.profile_url, params=self.profile_url_params, headers=headers
            )
            extra_data = _check_errors(response)
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(MicrosoftGraphOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(MicrosoftGraphOAuth2Adapter)
