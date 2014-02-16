from allauth.socialaccount.providers.oauth2.client import (OAuth2Client,
                                                           OAuth2Error)
try:
    from urllib.parse import parse_qsl, urlencode
except ImportError:
    from urllib import urlencode
    from urlparse import parse_qsl
import requests

class LinkedInOAuth2Client(OAuth2Client):
    def get_access_token(self, code):
        params = {'client_id': self.consumer_key,
                  'redirect_uri': self.callback_url,
                  'grant_type': 'authorization_code',
                  'client_secret': self.consumer_secret,
                  'scope': self.scope,
                  'code': code}
        url = self.access_token_url
        #NOTE: need to use GET instead of POST for linkedin
        #See: http://developer.linkedin.com/forum/unauthorized-invalid-or-expired-token-immediately-after-receiving-oauth2-token?page=1
        resp = requests.get(url, params=params)
        access_token = None
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
