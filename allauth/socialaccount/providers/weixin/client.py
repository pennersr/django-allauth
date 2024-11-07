from collections import OrderedDict

from django.utils.http import urlencode

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.client import (
    OAuth2Client,
    OAuth2Error,
)


class WeixinOAuth2Client(OAuth2Client):
    def get_redirect_url(self, authorization_url, scope, extra_params):
        scope = self.scope_delimiter.join(set(scope))
        params = {
            "appid": self.consumer_key,
            "redirect_uri": self.callback_url,
            "scope": scope,
            "response_type": "code",
        }
        if self.state:
            params["state"] = self.state
        params.update(extra_params)
        sorted_params = OrderedDict()
        for param in sorted(params):
            sorted_params[param] = params[param]
        return "%s?%s" % (authorization_url, urlencode(sorted_params))

    def get_access_token(self, code, pkce_code_verifier=None):
        data = {
            "appid": self.consumer_key,
            "grant_type": "authorization_code",
            "secret": self.consumer_secret,
            "code": code,
        }
        params = None
        self._strip_empty_keys(data)
        url = self.access_token_url
        if self.access_token_method == "GET":  # nosec
            params = data
            data = None
        if data and pkce_code_verifier:
            data["code_verifier"] = pkce_code_verifier
        # TODO: Proper exception handling
        resp = (
            get_adapter()
            .get_requests_session()
            .request(self.access_token_method, url, params=params, data=data)
        )
        access_token = None
        if resp.status_code == 200:
            access_token = resp.json()
        if not access_token or "access_token" not in access_token:
            raise OAuth2Error("Error retrieving access token: %s" % resp.content)
        return access_token
