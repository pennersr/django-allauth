try:
    from urllib.parse import parse_qsl, urlencode
except ImportError:
    from urllib import urlencode
    from urlparse import parse_qsl
import requests


class OAuth2Error(Exception):
    pass


class OAuth2Client(object):

    def __init__(self, request, consumer_key, consumer_secret,
                 authorization_url,
                 access_token_url,
                 callback_url,
                 scope,
                 extra_params):
        self.request = request
        self.authorization_url = authorization_url
        self.access_token_url = access_token_url
        self.callback_url = callback_url
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.scope = ' '.join(scope)
        self.state = None
        self.extra_params = extra_params

    def get_redirect_url(self):
        params = {
            'client_id': self.consumer_key,
            'redirect_uri': self.callback_url,
            'scope': self.scope,
            'response_type': 'code'
        }
        if self.state:
            params['state'] = self.state
        params.update(self.extra_params)
        return '%s?%s' % (self.authorization_url, urlencode(params))

    def get_access_token(self, code):
        params = {'client_id': self.consumer_key,
                  'redirect_uri': self.callback_url,
                  'grant_type': 'authorization_code',
                  'client_secret': self.consumer_secret,
                  'scope': self.scope,
                  'code': code}
        url = self.access_token_url
        # TODO: Proper exception handling
        resp = requests.post(url, params)
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
