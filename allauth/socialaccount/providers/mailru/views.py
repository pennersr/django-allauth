from hashlib import md5

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class MailRuOAuth2Adapter(OAuth2Adapter):
    provider_id = "mailru"
    access_token_url = "https://connect.mail.ru/oauth/token"  # nosec
    authorize_url = "https://connect.mail.ru/oauth/authorize"
    profile_url = "https://www.appsmail.ru/platform/api"

    def complete_login(self, request, app, token, **kwargs):
        uid = kwargs["response"]["x_mailru_vid"]
        data = {
            "method": "users.getInfo",
            "app_id": app.client_id,
            "secure": "1",
            "uids": uid,
        }
        param_list = sorted([f"{item}={data[item]}" for item in data])
        # See: https://api.mail.ru/docs/guides/restapi/
        data["sig"] = md5(
            ("".join(param_list) + app.secret).encode("utf-8")
        ).hexdigest()  # nosec
        with get_adapter().get_requests_session() as sess:
            response = sess.get(self.profile_url, params=data)
            extra_data = response.json()[0]
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(MailRuOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(MailRuOAuth2Adapter)
