from django.utils import simplejson
from django.contrib.auth.models import User

from allauth.socialaccount.providers.oauth.client import OAuth
from allauth.socialaccount.providers.oauth.views import (OAuthAdapter,
                                                         OAuthLoginView,
                                                         OAuthCallbackView)
from allauth.socialaccount.models import SocialLogin, SocialAccount

from provider import TwitterProvider


class TwitterAPI(OAuth):
    """
    Verifying twitter credentials
    """
    url = 'https://twitter.com/account/verify_credentials.json'

    def get_user_info(self):
        user = simplejson.loads(self.query(self.url))
        return user


class TwitterOAuthAdapter(OAuthAdapter):
    provider_id = TwitterProvider.id
    request_token_url = 'https://api.twitter.com/oauth/request_token'
    access_token_url = 'https://api.twitter.com/oauth/access_token'
    # Issue #42 -- this one authenticates over and over again...
    # authorize_url = 'https://api.twitter.com/oauth/authorize'
    authorize_url = 'https://api.twitter.com/oauth/authenticate'

    def complete_login(self, request, app, token):
        client = TwitterAPI(request, app.key, app.secret,
                            self.request_token_url)
        extra_data = client.get_user_info()
        uid = extra_data['id']
        user = User(username=extra_data['screen_name'])
        account = SocialAccount(user=user,
                                uid=uid,
                                provider=TwitterProvider.id,
                                extra_data=extra_data)
        return SocialLogin(account)


oauth_login = OAuthLoginView.adapter_view(TwitterOAuthAdapter)
oauth_callback = OAuthCallbackView.adapter_view(TwitterOAuthAdapter)

