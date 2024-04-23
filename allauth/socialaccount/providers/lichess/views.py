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

    access_token_url = "{0}/api/token".format(provider_base_url)
    authorize_url = "{0}/oauth".format(provider_base_url)

    profile_url = "{0}/api/account".format(provider_base_url)
    email_address_url = "{0}/api/account/email".format(provider_base_url)

    def complete_login(self, request, app, token, response):

        profile_res = get_adapter().get_requests_session().get(
            self.profile_url,
            params={"access_token": token.token},
            headers={"Authorization": f"Bearer {token.token}"},
        )

        profile_res.raise_for_status()
        extra_data = profile_res.json()
        
        user_profile = (
            extra_data["result"]
            if "result" in extra_data
            else extra_data
        )

        # retrieve email address if requested
        if QUERY_EMAIL:
            
            email_data = get_adapter().get_requests_session().get(
                self.email_address_url,
                headers={"Authorization": f"Bearer {token.token}"},
            )

            email_data.raise_for_status()
            email_data = email_data.json()

            # extract email address from response

            email = email_data.get("email", None)

            if email:
                user_profile["email"] = email

        return self.get_provider().sociallogin_from_response(request, user_profile)


oauth2_login = OAuth2LoginView.adapter_view(LichessOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(LichessOAuth2Adapter)
