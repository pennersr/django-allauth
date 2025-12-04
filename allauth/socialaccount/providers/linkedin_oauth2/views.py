from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class LinkedInOAuth2Adapter(OAuth2Adapter):
    provider_id = "linkedin_oauth2"
    access_token_url = "https://www.linkedin.com/oauth/v2/accessToken"  # nosec
    authorize_url = "https://www.linkedin.com/oauth/v2/authorization"
    profile_url = "https://api.linkedin.com/v2/me"
    email_url = "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))"  # noqa
    access_token_method = "GET"  # nosec

    def complete_login(self, request, app, token, **kwargs):
        extra_data = self.get_user_info(token)
        return self.get_provider().sociallogin_from_response(request, extra_data)

    def get_user_info(self, token):
        fields = self.get_provider().get_profile_fields()

        headers = {
            **self.get_provider().get_settings().get("HEADERS", {}),
            "Authorization": f"Bearer {token.token}",
        }

        info = {}
        with get_adapter().get_requests_session() as sess:
            if app_settings.QUERY_EMAIL:
                sess = get_adapter().get_requests_session()
                resp = sess.get(self.email_url, headers=headers)
                # If this response goes wrong, that is not a blocker in order to
                # continue.
                if resp.ok:
                    info = resp.json()

            url = f"{self.profile_url}?projection=({','.join(fields)})"
            resp = sess.get(url, headers=headers)
            resp.raise_for_status()
            info.update(resp.json())
        return info


oauth2_login = OAuth2LoginView.adapter_view(LinkedInOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(LinkedInOAuth2Adapter)
