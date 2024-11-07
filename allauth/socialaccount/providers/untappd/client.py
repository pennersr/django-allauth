from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.client import (
    OAuth2Client,
    OAuth2Error,
)


class UntappdOAuth2Client(OAuth2Client):
    """
    Custom client because Untappd:
        * uses redirect_url instead of redirect_uri
        * nests access_token inside an extra 'response' object
    """

    def get_access_token(self, code, pkce_code_verifier=None):
        from allauth.socialaccount.providers.untappd.provider import (
            UntappdProvider,
        )

        data = {
            "client_id": self.consumer_key,
            "redirect_url": self.callback_url,
            "grant_type": "authorization_code",
            "response_type": "code",
            "client_secret": self.consumer_secret,
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
        # Allow custom User Agent to comply with Untappd API
        settings = app_settings.PROVIDERS.get(UntappdProvider.id, {})
        headers = {"User-Agent": settings.get("USER_AGENT", "django-allauth")}
        # TODO: Proper exception handling
        resp = (
            get_adapter()
            .get_requests_session()
            .request(
                self.access_token_method,
                url,
                params=params,
                data=data,
                headers=headers,
            )
        )
        access_token = None
        if resp.status_code == 200:
            access_token = resp.json()["response"]
        if not access_token or "access_token" not in access_token:
            raise OAuth2Error("Error retrieving access token: %s" % resp.content)
        return access_token
