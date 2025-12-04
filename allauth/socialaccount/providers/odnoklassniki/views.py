from hashlib import md5

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


USER_FIELDS = [
    "age",
    "birthday",
    "current_status",
    "current_status_date",
    "current_status_id",
    "email",
    "first_name",
    "gender",
    "has_email",
    "last_name",
    "locale",
    "location",
    "name",
    "online",
    "photo_id",
    "pic1024x768",  # big
    "pic190x190",  # small
    "pic640x480",  # medium
    "pic_1",  # aka pic50x50
    "pic_2",  # aka pic128max
    "uid",
]


class OdnoklassnikiOAuth2Adapter(OAuth2Adapter):
    provider_id = "odnoklassniki"
    access_token_url = "https://api.odnoklassniki.ru/oauth/token.do"  # nosec
    authorize_url = "https://www.odnoklassniki.ru/oauth/authorize"
    profile_url = "https://api.odnoklassniki.ru/fb.do"
    access_token_method = "POST"  # nosec

    def complete_login(self, request, app, token, **kwargs):
        data = {
            "method": "users.getCurrentUser",
            "access_token": token.token,
            "fields": ",".join(USER_FIELDS),
            "format": "JSON",
            "application_key": app.key,
        }
        # Ondoklassniki prescribes a weak algo
        suffix = md5(
            f"{data['access_token']:s}{app.secret:s}".encode("utf-8")
        ).hexdigest()  # nosec
        check_list = sorted(
            [f"{k:s}={v:s}" for k, v in data.items() if k != "access_token"]
        )
        data["sig"] = md5(
            ("".join(check_list) + suffix).encode("utf-8")
        ).hexdigest()  # nosec

        with get_adapter().get_requests_session() as sess:
            response = sess.get(self.profile_url, params=data)
            extra_data = response.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(OdnoklassnikiOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(OdnoklassnikiOAuth2Adapter)
