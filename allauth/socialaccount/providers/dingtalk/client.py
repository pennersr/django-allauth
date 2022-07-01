import requests
from allauth.socialaccount.providers.oauth2.client import (
    OAuth2Client,
    OAuth2Error,
)


class DingtalkOAuth2Client(OAuth2Client):
    def get_access_token(self, code):
        data = {
            "clientId": self.consumer_key,
            "clientSecret": self.consumer_secret,
            "code": code,
            "grantType": "authorization_code"
        }
        params = None
        self._strip_empty_keys(data)
        url = self.access_token_url
        if self.access_token_method == "GET":
            params = data
            data = None
        resp = requests.request(self.access_token_method, url, params=params, data=data)
        access_token = None
        if resp.status_code == 200:
            access_token = resp.json()
        if not access_token or "accessToken" not in access_token:
            raise OAuth2Error("Error retrieving access token: %s" % resp.content)
        return access_token
