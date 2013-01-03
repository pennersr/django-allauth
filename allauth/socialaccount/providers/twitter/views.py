from django.utils import simplejson

from allauth.socialaccount.providers.oauth.client import OAuth
from allauth.socialaccount.providers.oauth.views import (OAuthAdapter,
                                                         OAuthLoginView,
                                                         OAuthCallbackView)
from allauth.socialaccount.models import SocialLogin, SocialAccount
from allauth.utils import get_user_model

from provider import TwitterProvider

User = get_user_model()

class TwitterAPI(OAuth):
    """
    Verifying twitter credentials
    """
    url = 'https://api.twitter.com/1.1/account/verify_credentials.json'

    def get_user_info(self):
        user = simplejson.loads(self.query(self.url))
        return user


class TwitterOAuthAdapter(OAuthAdapter):
    provider_id = TwitterProvider.id
    request_token_url = 'https://api.twitter.com/oauth/request_token'
    access_token_url = 'https://api.twitter.com/oauth/access_token'
    # Issue #42 -- this one authenticates over and over again...
    #authorize_url = 'https://api.twitter.com/oauth/authorize'
    authorize_url = 'https://api.twitter.com/oauth/authenticate'

    def complete_login(self, request, app, token):
        client = TwitterAPI(request, app.client_id, app.secret,
                            self.request_token_url)
        extra_data = client.get_user_info()
        uid = extra_data['id']
        user = User(username=extra_data['screen_name'])
        account = SocialAccount(user=user,
                                uid=uid,
                                provider=TwitterProvider.id,
                                extra_data=extra_data)
        return SocialLogin(account)

class TwitterFullAuthorizationAdapter(TwitterOAuthAdapter):
    authorize_url = 'https://api.twitter.com/oauth/authorize'


oauth_authorize = OAuthLoginView.adapter_view(TwitterFullAuthorizationAdapter)
oauth_login = OAuthLoginView.adapter_view(TwitterOAuthAdapter)
oauth_callback = OAuthCallbackView.adapter_view(TwitterOAuthAdapter)

