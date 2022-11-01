# -*- coding: utf-8 -*-
import requests

from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter


class OpenIDConnectAdapter(OAuth2Adapter):
    supports_state = True
    provider_id = "openid-connect"

    @property
    def openid_config(self):
        if not hasattr(self, "_openid_config"):
            resp = requests.get(self.get_provider().server_url)
            resp.raise_for_status()
            self._openid_config = resp.json()
        return self._openid_config

    @property
    def access_token_url(self):
        return self.openid_config["token_endpoint"]

    @property
    def authorize_url(self):
        return self.openid_config["authorization_endpoint"]

    @property
    def profile_url(self):
        return self.openid_config["userinfo_endpoint"]

    def complete_login(self, request, app, token, response):
        response = requests.get(
            self.profile_url, headers={"Authorization": "Bearer " + str(token)}
        )
        response.raise_for_status()
        extra_data = response.json()
        extra_data["id"] = extra_data["sub"]
        del extra_data["sub"]

        return self.get_provider().sociallogin_from_response(request, extra_data)
