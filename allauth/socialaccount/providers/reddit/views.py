from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class RedditAdapter(OAuth2Adapter):
    provider_id = "reddit"
    access_token_url = "https://www.reddit.com/api/v1/access_token"
    authorize_url = "https://www.reddit.com/api/v1/authorize"
    profile_url = "https://oauth.reddit.com/api/v1/me"
    basic_auth = True

    settings = app_settings.PROVIDERS.get(provider_id, {})
    # Allow custom User Agent to comply with reddit API limits
    headers = {"User-Agent": settings.get("USER_AGENT", "django-allauth-header")}

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": "bearer " + token.token}
        headers.update(self.headers)
        extra_data = (
            get_adapter().get_requests_session().get(self.profile_url, headers=headers)
        )

        # This only here because of weird response from the test suite
        if isinstance(extra_data, list):
            extra_data = extra_data[0]

        return self.get_provider().sociallogin_from_response(request, extra_data.json())


oauth2_login = OAuth2LoginView.adapter_view(RedditAdapter)
oauth2_callback = OAuth2CallbackView.adapter_view(RedditAdapter)
