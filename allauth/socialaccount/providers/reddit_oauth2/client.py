#===============================================================================
# This code contains a get_access_token method that overrides the method from
# oauth.client and works with Reddit.
# Author: Wendy Edwards (wayward710)
#===============================================================================
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
import requests
import requests.auth
try:
    from urllib.parse import parse_qsl, urlencode
except ImportError:
    from urllib import urlencode
    from urlparse import parse_qsl

class RedditOauth2Client(OAuth2Client):
    def get_access_token(self, code):
        # Add custom header here to avoid Reddit 429 error
        headers = {"User-Agent": "django-allauth-header"}
        # This code works with Reddit
        client_auth = requests.auth.HTTPBasicAuth(self.consumer_key,self.consumer_secret)
        post_data = {"grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.callback_url}
        url = self.access_token_url
        resp = requests.post(url,
            auth=client_auth,
            data=post_data,
            headers=headers)
        access_token = None
        
        # If we get a successful status code
        if resp.status_code == 200:
            # Weibo sends json via 'text/plain;charset=UTF-8'
            if (resp.headers['content-type'].split(';')[0] == 'application/json'
                or resp.text[:2] == '{"'):
                access_token = resp.json()
            else:
                access_token = dict(parse_qsl(resp.text))
        if not access_token or 'access_token' not in access_token:
            raise OAuth2Error('Error retrieving access token: %s'
                              % resp.content)
        return access_token