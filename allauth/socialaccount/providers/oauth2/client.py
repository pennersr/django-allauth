import requests
from urllib.parse import parse_qsl

from django.utils.http import urlencode

from allauth.socialaccount.adapter import get_adapter


class OAuth2Error(Exception):
    pass


class OAuth2Client:
    client_id_parameter = "client_id"

    def __init__(
        self,
        request,
        consumer_key,
        consumer_secret,
        access_token_method,
        access_token_url,
        callback_url,
        scope_delimiter=" ",
        headers=None,
        basic_auth=False,
    ):
        self.request = request
        self.access_token_method = access_token_method
        self.access_token_url = access_token_url
        self.callback_url = callback_url
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.scope_delimiter = scope_delimiter
        self.state = None
        self.headers = headers
        self.basic_auth = basic_auth

    def get_redirect_url(self, authorization_url, scope, extra_params):
        scope = self.scope_delimiter.join(set(scope))
        params = {
            self.client_id_parameter: self.consumer_key,
            "redirect_uri": self.callback_url,
            "scope": scope,
            "response_type": "code",
        }
        if self.state:
            params["state"] = self.state
        params.update(extra_params)
        return "%s?%s" % (authorization_url, urlencode(params))

    def get_access_token(self, code, pkce_code_verifier=None):
        data = {
            "redirect_uri": self.callback_url,
            "grant_type": "authorization_code",
            "code": code,
        }
        if self.basic_auth:
            auth = requests.auth.HTTPBasicAuth(self.consumer_key, self.consumer_secret)
        else:
            auth = None
            data.update(
                {
                    self.client_id_parameter: self.consumer_key,
                    "client_secret": self.consumer_secret,
                }
            )
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
            .request(
                self.access_token_method,
                url,
                params=params,
                data=data,
                headers=self.headers,
                auth=auth,
            )
        )

        access_token = None
        if resp.status_code in [200, 201]:
            # Weibo sends json via 'text/plain;charset=UTF-8'
            if (
                resp.headers["content-type"].split(";")[0] == "application/json"
                or resp.text[:2] == '{"'
            ):
                access_token = resp.json()
            else:
                access_token = dict(parse_qsl(resp.text))
        if not access_token or "access_token" not in access_token:
            raise OAuth2Error("Error retrieving access token: %s" % resp.content)
        return access_token

    def _strip_empty_keys(self, params):
        """Added because the Dropbox OAuth2 flow doesn't
        work when scope is passed in, which is empty.
        """
        keys = [k for k, v in params.items() if v == ""]
        for key in keys:
            del params[key]
