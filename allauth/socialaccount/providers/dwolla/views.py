from django.conf import settings

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import DwollaProvider


ENVIRONMENTS = {
    "production": {
        "auth_url": "https://www.dwolla.com/oauth/v2/authenticate",
        "token_url": "https://www.dwolla.com/oauth/v2/token",
    },
    "sandbox": {
        "auth_url": "https://uat.dwolla.com/oauth/v2/authenticate",
        "token_url": "https://uat.dwolla.com/oauth/v2/token",
    },
}

ENV = (
    getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
    .get("dwolla", {})
    .get("ENVIRONMENT", "production")
)

AUTH_URL = ENVIRONMENTS[ENV]["auth_url"]
TOKEN_URL = ENVIRONMENTS[ENV]["token_url"]


class DwollaOAuth2Adapter(OAuth2Adapter):
    """Dwolla Views Adapter"""

    scope_delimiter = "|"

    provider_id = DwollaProvider.id
    access_token_url = TOKEN_URL
    authorize_url = AUTH_URL

    def complete_login(self, request, app, token, response, **kwargs):
        resp = (
            get_adapter()
            .get_requests_session()
            .get(
                response["_links"]["account"]["href"],
                headers={
                    "authorization": "Bearer %s" % token.token,
                    "accept": "application/vnd.dwolla.v1.hal+json",
                },
            )
        )

        extra_data = resp.json()

        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(DwollaOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(DwollaOAuth2Adapter)
