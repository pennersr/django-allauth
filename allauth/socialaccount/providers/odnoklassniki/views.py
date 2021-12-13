import requests
from hashlib import md5

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import OdnoklassnikiProvider


USER_FIELDS = [
    "uid",
    "locale",
    "first_name",
    "last_name",
    "name",
    "gender",
    "age",
    "birthday",
    "has_email",
    "current_status",
    "current_status_id",
    "current_status_date",
    "online",
    "photo_id",
    "pic_1",  # aka pic50x50
    "pic_2",  # aka pic128max
    "pic190x190",  # small
    "pic640x480",  # medium
    "pic1024x768",  # big
    "location",
]


class OdnoklassnikiOAuth2Adapter(OAuth2Adapter):
    provider_id = OdnoklassnikiProvider.id
    access_token_url = "https://api.odnoklassniki.ru/oauth/token.do"
    authorize_url = "https://www.odnoklassniki.ru/oauth/authorize"
    profile_url = "https://api.odnoklassniki.ru/fb.do"
    access_token_method = "POST"

    def complete_login(self, request, app, token, **kwargs):
        data = {
            "method": "users.getCurrentUser",
            "access_token": token.token,
            "fields": ",".join(USER_FIELDS),
            "format": "JSON",
            "application_key": app.key,
        }
        suffix = md5(
            "{0:s}{1:s}".format(data["access_token"], app.secret).encode("utf-8")
        ).hexdigest()
        check_list = sorted(
            ["{0:s}={1:s}".format(k, v) for k, v in data.items() if k != "access_token"]
        )
        data["sig"] = md5(("".join(check_list) + suffix).encode("utf-8")).hexdigest()

        response = requests.get(self.profile_url, params=data)
        extra_data = response.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(OdnoklassnikiOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(OdnoklassnikiOAuth2Adapter)
