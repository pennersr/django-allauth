from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.models import SocialToken
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class AmazonCognitoOAuth2Adapter(OAuth2Adapter):
    provider_id = "amazon_cognito"

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
        return f"{self.domain}/oauth2/token"

    @property
    def authorize_url(self):
        return f"{self.domain}/oauth2/authorize"

    @property
    def profile_url(self):
        return f"{self.domain}/oauth2/userInfo"

    def complete_login(self, request, app, token: SocialToken, **kwargs):
        headers = {
            "Authorization": f"Bearer {token.token}",
        }
        with get_adapter().get_requests_session() as sess:
            response = sess.get(self.profile_url, headers=headers)
            response.raise_for_status()
            extra_data = response.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(AmazonCognitoOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(AmazonCognitoOAuth2Adapter)
