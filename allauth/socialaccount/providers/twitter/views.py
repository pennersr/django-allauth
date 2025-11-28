from allauth.socialaccount.app_settings import QUERY_EMAIL
from allauth.socialaccount.providers.oauth.client import OAuth
from allauth.socialaccount.providers.oauth.views import (
    OAuthAdapter,
    OAuthCallbackView,
    OAuthLoginView,
)


class TwitterAPI(OAuth):
    """
    Verifying twitter credentials
    """

    _base_url = "https://api.x.com/1.1/account/verify_credentials.json"
    url = f"{_base_url}?include_email=true" if QUERY_EMAIL else _base_url

    def get_user_info(self):
        user = self.query(self.url).json()
        return user


class TwitterOAuthAdapter(OAuthAdapter):
    provider_id = "twitter"
    request_token_url = "https://api.x.com/oauth/request_token"  # nosec
    access_token_url = "https://api.x.com/oauth/access_token"  # nosec
    # Issue #42 -- this one authenticates over and over again...
    # authorize_url = 'https://api.twitter.com/oauth/authorize'
    authorize_url = "https://api.x.com/oauth/authenticate"

    def complete_login(self, request, app, token, response):
        client = TwitterAPI(request, app.client_id, app.secret, self.request_token_url)
        extra_data = client.get_user_info()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth_login = OAuthLoginView.adapter_view(TwitterOAuthAdapter)
oauth_callback = OAuthCallbackView.adapter_view(TwitterOAuthAdapter)
