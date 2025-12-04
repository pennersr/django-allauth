from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.app_settings import QUERY_EMAIL
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class LichessOAuth2Adapter(OAuth2Adapter):
    provider_id = "lichess"

    settings = app_settings.PROVIDERS.get(provider_id, {})
    provider_base_url = settings.get("API_URL", "https://lichess.org")

    access_token_url = f"{provider_base_url}/api/token"
    authorize_url = f"{provider_base_url}/oauth"

    profile_url = f"{provider_base_url}/api/account"
    email_address_url = f"{provider_base_url}/api/account/email"

    def complete_login(self, request, app, token, response):
        headers = {"Authorization": f"Bearer {token.token}"}
        with get_adapter().get_requests_session() as sess:
            profile_res = sess.get(
                self.profile_url,
                params={"access_token": token.token},
                headers=headers,
            )
            profile_res.raise_for_status()
            extra_data = profile_res.json()

            user_profile = (
                extra_data["result"] if "result" in extra_data else extra_data
            )

            # retrieve email address if requested
            if QUERY_EMAIL:
                email_resp = sess.get(self.email_address_url, headers=headers)

                email_resp.raise_for_status()
                email_data = email_resp.json()

                # extract email address from response

                email = email_data.get("email", None)

                if email:
                    user_profile["email"] = email

        return self.get_provider().sociallogin_from_response(request, user_profile)


oauth2_login = OAuth2LoginView.adapter_view(LichessOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(LichessOAuth2Adapter)
