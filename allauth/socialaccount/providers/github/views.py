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
        api_url = "{0}/api/v3".format(web_url)
    else:
        web_url = "https://github.com"
        api_url = "https://api.github.com"

    access_token_url = "{0}/login/oauth/access_token".format(web_url)
    authorize_url = "{0}/login/oauth/authorize".format(web_url)
    profile_url = "{0}/user".format(api_url)
    emails_url = "{0}/user/emails".format(api_url)

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": "token {}".format(token.token)}
        resp = (
            get_adapter().get_requests_session().get(self.profile_url, headers=headers)
        )
        resp.raise_for_status()
        extra_data = resp.json()
        if app_settings.QUERY_EMAIL and not extra_data.get("email"):
            emails = self.get_emails(headers)
            if emails:
                extra_data["emails"] = emails
        return self.get_provider().sociallogin_from_response(request, extra_data)

    def get_emails(self, headers):
        resp = (
            get_adapter().get_requests_session().get(self.emails_url, headers=headers)
        )
        # https://api.github.com/user/emails -- 404 is documented to occur.
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()


oauth2_login = OAuth2LoginView.adapter_view(GitHubOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(GitHubOAuth2Adapter)
