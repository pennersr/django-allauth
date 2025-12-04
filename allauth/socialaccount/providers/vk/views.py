import uuid
from requests import RequestException

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)
from allauth.utils import get_request_param


class VKOAuth2Adapter(OAuth2Adapter):
    provider_id = "vk"
    access_token_url = "https://id.vk.ru/oauth2/auth"  # nosec
    authorize_url = "https://id.vk.ru/authorize"
    profile_url = "https://id.vk.ru/oauth2/user_info"

    def get_access_token_data(self, request, app, client, pkce_code_verifier=None):
        code = get_request_param(self.request, "code")
        device_id = get_request_param(self.request, "device_id")
        extra_data = {
            # "state" isn't strictly necessary for now, but since VK ID documentation doesn't
            # specify required vs optional parameters at all, we still add this (now optional)
            # param to make the code less fragile for future, when they may start requiring it
            "state": str(uuid.uuid4()),
            "device_id": device_id,
        }
        data = client.get_access_token(
            code, pkce_code_verifier=pkce_code_verifier, extra_data=extra_data
        )
        self.did_fetch_access_token = True
        return data

    def complete_login(self, request, app, token, **kwargs):
        req_data = {
            "access_token": token.token,
            "client_id": app.client_id,
        }
        with get_adapter().get_requests_session() as sess:
            resp = sess.post(self.profile_url, data=req_data)
            resp.raise_for_status()
            resp_data = resp.json()
        if "error" in resp_data or "user" not in resp_data:
            raise RequestException(
                "Could not get basic data for user being authenticated"
            )
        return self.get_provider().sociallogin_from_response(request, resp_data["user"])


oauth2_login = OAuth2LoginView.adapter_view(VKOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(VKOAuth2Adapter)
