import json

from allauth.socialaccount.providers.oauth.client import OAuth
from allauth.socialaccount.providers.oauth.views import (OAuthAdapter,
                                                         OAuthLoginView,
                                                         OAuthCallbackView)

from .provider import BitbucketProvider


class BitbucketAPI(OAuth):

    emails_url = 'https://bitbucket.org/api/1.0/emails/'
    users_url = 'https://bitbucket.org/api/1.0/users/'

    def get_user_info(self):
        # TODO: Actually turn these into EmailAddress
        emails = json.loads(self.query(self.emails_url))
        for address in reversed(emails):
            if address['active']:
                email = address['email']
                if address['primary']:
                    break
        data = json.loads(self.query(self.users_url + email))
        user = data['user']
        return user


class BitbucketOAuthAdapter(OAuthAdapter):
    provider_id = BitbucketProvider.id
    request_token_url = 'https://bitbucket.org/api/1.0/oauth/request_token'
    access_token_url = 'https://bitbucket.org/api/1.0/oauth/access_token'
    authorize_url = 'https://bitbucket.org/api/1.0/oauth/authenticate'

    def complete_login(self, request, app, token):
        client = BitbucketAPI(request, app.client_id, app.secret,
                              self.request_token_url)
        extra_data = client.get_user_info()
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)

oauth_login = OAuthLoginView.adapter_view(BitbucketOAuthAdapter)
oauth_callback = OAuthCallbackView.adapter_view(BitbucketOAuthAdapter)
