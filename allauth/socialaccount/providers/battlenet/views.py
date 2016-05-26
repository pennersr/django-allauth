"""
OAuth2 Adapter for Battle.net

Resources:

* Battle.net OAuth2 documentation:
    https://dev.battle.net/docs/read/oauth
* Battle.net API documentation:
    https://dev.battle.net/io-docs
* Original announcement:
    https://us.battle.net/en/forum/topic/13979297799
* The Battle.net API forum:
    https://us.battle.net/en/forum/15051532/
"""
import requests
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter, OAuth2CallbackView, OAuth2LoginView
)
from .provider import BattleNetProvider


class BattleNetOAuth2Adapter(OAuth2Adapter):
    """
    OAuth2 adapter for Battle.net
    https://dev.battle.net/docs/read/oauth

    Region is set to us by default.
    Set the `battlenet_region` attribute to change it.
    Can be any of eu, us, kr, sea, tw or cn
    """
    provider_id = BattleNetProvider.id
    supports_state = True
    battlenet_region = "us"

    @property
    def battlenet_base_url(self):
        region = self.battlenet_region
        if region == "cn":
            return "https://www.battlenet.com.cn"
        return "https://%s.battle.net" % ("us" if region == "sea" else region)

    @property
    def battlenet_api_url(self):
        return "https://%s.api.battle.net" % (self.battlenet_region)

    @property
    def access_token_url(self):
        return self.battlenet_base_url + "/oauth/token"

    @property
    def authorize_url(self):
        return self.battlenet_base_url + "/oauth/authorize"

    @property
    def profile_url(self):
        return self.battlenet_api_url + "/account/user"

    def complete_login(self, request, app, token, **kwargs):
        params = {"access_token": token.token}
        response = requests.get(self.profile_url, params=params)
        data = response.json()
        return self.get_provider().sociallogin_from_response(request, data)

oauth2_login = OAuth2LoginView.adapter_view(BattleNetOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(BattleNetOAuth2Adapter)
