from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class EdxOAuth2Adapter(OAuth2Adapter):
    provider_id = "edx"
    provider_default_url = "https://edx.org"

    settings = app_settings.PROVIDERS.get(provider_id, {})
    provider_base_url = settings.get("EDX_URL", provider_default_url)

    access_token_url = f"{provider_base_url}/oauth2/access_token"
    authorize_url = f"{provider_base_url}/oauth2/authorize/"
    profile_url = f"{provider_base_url}/api/user/v1/me"
    account_url = "{0}/api/user/v1/accounts/{1}"
    supports_state = False
    redirect_uri_protocol = "https"

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": f"Bearer {token.token}"}
        with get_adapter().get_requests_session() as sess:
            response = sess.get(self.profile_url, headers=headers)
            extra_data = response.json()

            if extra_data.get("email", None) is None:
                account_url = self.account_url.format(
                    self.provider_base_url, extra_data["username"]
                )
                response = sess.get(account_url, headers=headers)
                extra_data = response.json()

        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(EdxOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(EdxOAuth2Adapter)
