from django.utils import simplejson

from allauth.socialaccount.providers.oauth.client import OAuth
from allauth.socialaccount.providers.oauth.views import (OAuthAdapter,
                                                         OAuthLoginView,
                                                         OAuthCallbackView,
                                                         OAuthCompleteView)


from models import TwitterProvider

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
    authorize_url = 'https://api.twitter.com/oauth/authorize'
        
    def get_user_info(self, request, app):
        client = TwitterAPI(request, app.key, app.secret, 
                            self.request_token_url)
        user_info = client.get_user_info()
        uid = user_info['id']
        extra_data = { 'profile_image_url': user_info['profile_image_url'],
                       'screen_name': user_info['screen_name'] }
        data = dict(twitter_user_info=user_info,
                    username=user_info['screen_name'])
        return uid, data, extra_data


oauth_login = OAuthLoginView.adapter_view(TwitterOAuthAdapter)
oauth_callback = OAuthCallbackView.adapter_view(TwitterOAuthAdapter)
oauth_complete = OAuthCompleteView.adapter_view(TwitterOAuthAdapter)

