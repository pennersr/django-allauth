from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class BasecampOAuth2Adapter(OAuth2Adapter):
    provider_id = "basecamp"
    access_token_url = (
        "https://launchpad.37signals.com/authorization/token?type=web_server"  # noqa
    )
    authorize_url = "https://launchpad.37signals.com/authorization/new"
    profile_url = "https://launchpad.37signals.com/authorization.json"

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": "Bearer {0}".format(token.token)}
        resp = (
            get_adapter().get_requests_session().get(self.profile_url, headers=headers)
        )
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(BasecampOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(BasecampOAuth2Adapter)
