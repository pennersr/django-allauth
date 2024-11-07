from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class WeiboOAuth2Adapter(OAuth2Adapter):
    provider_id = "weibo"
    access_token_url = "https://api.weibo.com/oauth2/access_token"  # nosec
    authorize_url = "https://api.weibo.com/oauth2/authorize"
    profile_url = "https://api.weibo.com/2/users/show.json"

    def complete_login(self, request, app, token, **kwargs):
        uid = kwargs.get("response", {}).get("uid")
        resp = (
            get_adapter()
            .get_requests_session()
            .get(self.profile_url, params={"access_token": token.token, "uid": uid})
        )
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(WeiboOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(WeiboOAuth2Adapter)
