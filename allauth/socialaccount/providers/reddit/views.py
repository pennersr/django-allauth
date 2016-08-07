import requests

from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)
from .provider import RedditProvider


class RedditAdapter(OAuth2Adapter):
    provider_id = RedditProvider.id
    access_token_url = 'https://www.reddit.com/api/v1/access_token'
    authorize_url = 'https://www.reddit.com/api/v1/authorize'
    profile_url = 'https://oauth.reddit.com/api/v1/me'
    basic_auth = True
    headers = {"User-Agent": "django-allauth-header"}

    # After successfully logging in, use access token to retrieve user info
    def complete_login(self, request, app, token, **kwargs):
        headers = {
            "Authorization": "bearer " + token.token}
        headers.update(self.headers)
        extra_data = requests.get(self.profile_url, headers=headers)

        # This only here because of weird response from the test suite
        if isinstance(extra_data, list):
            extra_data = extra_data[0]

        return self.get_provider().sociallogin_from_response(
            request,
            extra_data.json()
        )


oauth2_login = OAuth2LoginView.adapter_view(RedditAdapter)
oauth2_callback = OAuth2CallbackView.adapter_view(RedditAdapter)
