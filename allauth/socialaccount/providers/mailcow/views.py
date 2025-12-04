from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)
from allauth.utils import get_request_param


class MailcowAdapter(OAuth2Adapter):
    provider_id = "mailcow"
    settings = app_settings.PROVIDERS.get(provider_id, {})
    server = settings.get("SERVER", "https://hosted.mailcow.de")
    access_token_url = f"{server}/oauth/token"
    authorize_url = f"{server}/oauth/authorize"
    profile_url = f"{server}/oauth/profile"

    def complete_login(self, request, app, token, **kwargs):
        code = get_request_param(request, "code")
        extra_data = self.get_user_info(token.token, code)
        return self.get_provider().sociallogin_from_response(request, extra_data)

    def get_user_info(self, access_token, code):
        with get_adapter().get_requests_session() as sess:
            params = {"access_token": access_token, "code": code}
            resp = sess.get(self.profile_url, params=params)
            resp.raise_for_status()
        return resp.json()


oauth2_login = OAuth2LoginView.adapter_view(MailcowAdapter)
oauth2_callback = OAuth2CallbackView.adapter_view(MailcowAdapter)
