from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client, OAuth2Error


class DingTalkOAuth2Client(OAuth2Client):
    def get_access_token(self, code, pkce_code_verifier=None):
        data = {
            "clientId": self.consumer_key,
            "clientSecret": self.consumer_secret,
            "code": code,
            "grantType": "authorization_code",
        }
        params = None
        if pkce_code_verifier:
            data["code_verifier"] = pkce_code_verifier
        self._strip_empty_keys(data)
        url = self.access_token_url
        if self.access_token_method == "GET":  # nosec
            params = data
            data = None
        resp = (
            get_adapter()
            .get_requests_session()
            .request(self.access_token_method, url, params=params, json=data)
        )
        resp.raise_for_status()
        access_token = resp.json()
        if not access_token or "accessToken" not in access_token:
            raise OAuth2Error("Error retrieving access token: %s" % resp.content)

        access_token["access_token"] = access_token.pop("accessToken")
        access_token["refresh_token"] = access_token.pop("refreshToken")
        access_token["expires_in"] = access_token.pop("expireIn")
        return access_token
