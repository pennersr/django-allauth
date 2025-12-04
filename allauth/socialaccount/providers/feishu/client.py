import json
from collections import OrderedDict

from django.utils.http import urlencode

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client, OAuth2Error


class FeishuOAuth2Client(OAuth2Client):
    app_access_token_url = (
        "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal/"  # nosec
    )

    def get_redirect_url(self, authorization_url, scope, extra_params):
        scope = self.scope_delimiter.join(set(scope))
        params = {
            "app_id": self.consumer_key,
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
        return f"{authorization_url}?{urlencode(sorted_params)}"

    def app_access_token(self):
        data = {
            "app_id": self.consumer_key,
            "app_secret": self.consumer_secret,
        }

        self._strip_empty_keys(data)
        url = self.app_access_token_url

        # TODO: Proper exception handling
        with get_adapter().get_requests_session() as sess:
            resp = sess.request("POST", url, data=data)
            resp.raise_for_status()
            access_token = resp.json()
        if not access_token or "app_access_token" not in access_token:
            raise OAuth2Error(f"Error retrieving app access token: {resp.content}")
        return access_token["app_access_token"]

    def get_access_token(self, code, pkce_code_verifier=None):
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "app_access_token": self.app_access_token(),
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
        with get_adapter().get_requests_session() as sess:
            resp = sess.request(
                self.access_token_method,
                url,
                params=params,
                data=json.dumps(data),
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()
            access_token = resp.json()
        if (
            not access_token
            or "data" not in access_token
            or "access_token" not in access_token["data"]
        ):
            raise OAuth2Error(f"Error retrieving access token: {resp.content}")
        return access_token["data"]
