from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class RedditAdapter(OAuth2Adapter):
    provider_id = "reddit"
    access_token_url = "https://www.reddit.com/api/v1/access_token"  # nosec
    authorize_url = "https://www.reddit.com/api/v1/authorize"
    profile_url = "https://oauth.reddit.com/api/v1/me"
    basic_auth = True

    settings = app_settings.PROVIDERS.get(provider_id, {})
    # Allow custom User Agent to comply with reddit API limits
    headers = {"User-Agent": settings.get("USER_AGENT", "django-allauth-header")}

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": f"bearer {token.token}", **self.headers}
        with get_adapter().get_requests_session() as sess:
            resp = sess.get(self.profile_url, headers=headers)

            # This only here because of weird response from the test suite
            if isinstance(resp, list):
                resp = resp[0]

            extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(RedditAdapter)
oauth2_callback = OAuth2CallbackView.adapter_view(RedditAdapter)
