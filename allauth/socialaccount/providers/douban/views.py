from django.utils.translation import gettext_lazy as _

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from ..base import ProviderException
from .provider import DoubanProvider


class DoubanOAuth2Adapter(OAuth2Adapter):
    provider_id = DoubanProvider.id
    access_token_url = "https://www.douban.com/service/auth2/token"
    authorize_url = "https://www.douban.com/service/auth2/auth"
    profile_url = "https://api.douban.com/v2/user/~me"

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": "Bearer %s" % token.token}
        resp = (
            get_adapter().get_requests_session().get(self.profile_url, headers=headers)
        )
        extra_data = resp.json()
        """
        Douban may return data like this:

            {
                'code': 128,
                'request': 'GET /v2/user/~me',
                'msg': 'user_is_locked:53358092'
            }

        """
        if "id" not in extra_data:
            msg = extra_data.get("msg", _("Invalid profile data"))
            raise ProviderException(msg)
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(DoubanOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(DoubanOAuth2Adapter)
