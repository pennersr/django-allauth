from http import HTTPStatus
from typing import Optional

from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class GitHubOAuth2Adapter(OAuth2Adapter):
    provider_id = "github"
    settings = app_settings.PROVIDERS.get(provider_id, {})

    if "GITHUB_URL" in settings:
        web_url = settings.get("GITHUB_URL").rstrip("/")
        api_url = f"{web_url}/api/v3"
    else:
        web_url = "https://github.com"
        api_url = "https://api.github.com"

    access_token_url = f"{web_url}/login/oauth/access_token"
    authorize_url = f"{web_url}/login/oauth/authorize"
    profile_url = f"{api_url}/user"
    emails_url = f"{api_url}/user/emails"

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": f"token {token.token}"}
        with get_adapter().get_requests_session() as sess:
            resp = sess.get(self.profile_url, headers=headers)
            resp.raise_for_status()
            extra_data = resp.json()
        if app_settings.QUERY_EMAIL:
            if emails := self.get_emails(headers):
                extra_data["emails"] = emails
        return self.get_provider().sociallogin_from_response(request, extra_data)

    def get_emails(self, headers) -> Optional[list]:
        with get_adapter().get_requests_session() as sess:
            resp = sess.get(self.emails_url, headers=headers)
            # https://api.github.com/user/emails -- 404 is documented to occur.
            if resp.status_code == HTTPStatus.NOT_FOUND:
                return None
            resp.raise_for_status()
            return resp.json()


oauth2_login = OAuth2LoginView.adapter_view(GitHubOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(GitHubOAuth2Adapter)
