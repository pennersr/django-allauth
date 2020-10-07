import requests

from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.amazon_cognito.provider import (
    AmazonCognitoProvider,
)
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class AmazonCognitoOAuth2Adapter(OAuth2Adapter):
    provider_id = AmazonCognitoProvider.id

    DOMAIN_KEY_MISSING_ERROR = (
        '"DOMAIN" key is missing in Amazon Cognito configuration.'
    )

    @property
    def settings(self):
        return app_settings.PROVIDERS.get(self.provider_id, {})

    @property
    def domain(self):
        domain = self.settings.get("DOMAIN")

        if domain is None:
            raise ValueError(self.DOMAIN_KEY_MISSING_ERROR)

        return domain

    @property
    def access_token_url(self):
        return "{}/oauth2/token".format(self.domain)

    @property
    def authorize_url(self):
        return "{}/oauth2/authorize".format(self.domain)

    @property
    def profile_url(self):
        return "{}/oauth2/userInfo".format(self.domain)

    def complete_login(self, request, app, access_token, **kwargs):
        headers = {
            "Authorization": "Bearer {}".format(access_token),
        }
        extra_data = requests.get(self.profile_url, headers=headers)
        extra_data.raise_for_status()

        return self.get_provider().sociallogin_from_response(request, extra_data.json())


oauth2_login = OAuth2LoginView.adapter_view(AmazonCognitoOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(AmazonCognitoOAuth2Adapter)
