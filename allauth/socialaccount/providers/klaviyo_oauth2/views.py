import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)
from django.conf import settings

from .provider import KlaviyoProvider


ACCESS_TOKEN_URL = (
    getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
    .get("", {})
    .get("ACCESS_TOKEN_URL", "https://a.klaviyo.com/oauth/token")
)

AUTHORIZE_URL = (
    getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
    .get("", {})
    .get("AUTHORIZE_URL", "https://www.klaviyo.com/oauth/authorize")
)

KLAVIYO_API_VERSION = '2023-10-15'


class KlaviyoOAuth2Adapter(OAuth2Adapter):
    provider_id = KlaviyoProvider.id
    access_token_url = ACCESS_TOKEN_URL
    authorize_url = AUTHORIZE_URL
    basic_auth = True

    def complete_login(self, request, app, access_token, **kwargs):
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "revision": KLAVIYO_API_VERSION,
            "Authorization": f'Bearer {access_token.token}',
        }
        r = requests.get(
            'https://a.klaviyo.com/api/accounts/',
            headers=headers,
        )
        extra_data = r.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(KlaviyoOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(KlaviyoOAuth2Adapter)
