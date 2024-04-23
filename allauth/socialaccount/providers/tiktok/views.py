from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)
from allauth.socialaccount.providers.tiktok.client import TiktokOAuth2Client


class TiktokOAuth2Adapter(OAuth2Adapter):
    provider_id = "tiktok"
    access_token_url = "https://open.tiktokapis.com/v2/oauth/token/"
    authorize_url = "https://www.tiktok.com/v2/auth/authorize/"
    # https://developers.tiktok.com/doc/tiktok-api-v2-get-user-info/
    profile_url = "https://open.tiktokapis.com/v2/user/info/"
    client_class = TiktokOAuth2Client

    def get_query_fields(self):
        fields = ""
        if "user.info.basic" in self.get_provider().get_scope():
            fields = "open_id,display_name,avatar_url"
        if "user.info.profile" in self.get_provider().get_scope():
            fields += ",username,profile_deep_link"
        return fields

    def complete_login(self, request, app, token, **kwargs):
        headers = {
            "Authorization": "Bearer {}".format(token.token),
            "Client-ID": app.client_id,
        }
        params = {"fields": self.get_query_fields()}
        response = (
            get_adapter().get_requests_session().get(self.profile_url, headers=headers, params=params)
        )

        data = response.json()
        if response.status_code >= 400:
            error = data.get("error", "")
            message = data.get("message", "")
            raise OAuth2Error("Tiktok API Error: %s (%s)" % (error, message))

        try:
            user_info = data.get("data", [])[0]
        except IndexError:
            raise OAuth2Error("Invalid data from Tiktok API: %s" % (data))

        if "id" not in user_info:
            raise OAuth2Error("Invalid data from Tiktok API: %s" % (user_info))

        return self.get_provider().sociallogin_from_response(request, user_info)


oauth2_login = OAuth2LoginView.adapter_view(TiktokOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(TiktokOAuth2Adapter)
