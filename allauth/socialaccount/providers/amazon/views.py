import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import AmazonProvider


class AmazonOAuth2Adapter(OAuth2Adapter):
    provider_id = AmazonProvider.id
    access_token_url = "https://api.amazon.com/auth/o2/token"
    authorize_url = "http://www.amazon.com/ap/oa"
    profile_url = "https://api.amazon.com/user/profile"
    supports_state = False

    def complete_login(self, request, app, token, **kwargs):
        response = requests.get(self.profile_url, params={"access_token": token})
        extra_data = response.json()
        if "Profile" in extra_data:
            extra_data = {
                "user_id": extra_data["Profile"]["CustomerId"],
                "name": extra_data["Profile"]["Name"],
                "email": extra_data["Profile"]["PrimaryEmail"],
            }
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(AmazonOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(AmazonOAuth2Adapter)
