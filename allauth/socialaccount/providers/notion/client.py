from requests.auth import HTTPBasicAuth
from urllib.parse import parse_qsl

from django.utils.http import urlencode

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client, OAuth2Error


class NotionOAuth2Client(OAuth2Client):
    def get_redirect_url(self, authorization_url, scope, extra_params):
        scope = self.scope_delimiter.join(set(scope))
        params = {
            "client_id": self.consumer_key,
            "scope": scope,
            "response_type": "code",
            "owner": "user",
        }
        if self.state:
            params["state"] = self.state
        return "%s?%s" % (authorization_url, urlencode(params))

    def get_access_token(self, code, pkce_code_verifier=None):
        resp = (
            get_adapter()
            .get_requests_session()
            .request(
                self.access_token_method,
                self.access_token_url,
                auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret),
                json={"code": code, "grant_type": "authorization_code"},
                headers=self.headers,
            )
        )
        access_token = None
        if resp.status_code in [200, 201]:
            try:
                access_token = resp.json()
            except ValueError:
                access_token = dict(parse_qsl(resp.text))
        if not access_token or "access_token" not in access_token:
            raise OAuth2Error("Error retrieving access token: %s" % resp.content)
        return access_token
