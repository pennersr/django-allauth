import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import DisqusProvider


class DisqusOAuth2Adapter(OAuth2Adapter):
    provider_id = DisqusProvider.id
    access_token_url = "https://disqus.com/api/oauth/2.0/access_token/"
    authorize_url = "https://disqus.com/api/oauth/2.0/authorize/"
    profile_url = "https://disqus.com/api/3.0/users/details.json"
    scope_delimiter = ","

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(
            self.profile_url,
            params={
                "access_token": token.token,
                "api_key": app.client_id,
                "api_secret": app.secret,
            },
        )
        resp.raise_for_status()

        extra_data = resp.json().get("response")

        login = self.get_provider().sociallogin_from_response(request, extra_data)
        return login


oauth2_login = OAuth2LoginView.adapter_view(DisqusOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(DisqusOAuth2Adapter)
