import urllib
import urlparse
import httplib2
import json

class OAuth2Error(Exception):
    pass


class OAuth2Client(object):

    def __init__(self, request, consumer_key, consumer_secret,
                 authorization_url,
                 access_token_url,
                 callback_url,
                 scope):
        self.request = request
        self.authorization_url = authorization_url
        self.access_token_url = access_token_url
        self.callback_url = callback_url
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.scope = ' '.join(scope)

    def get_redirect_url(self):
        params = {
            'client_id': self.consumer_key,
            'redirect_uri': self.callback_url,
            'scope': self.scope,
            'response_type': 'code'
        }
        return '%s?%s' % (self.authorization_url, urllib.urlencode(params))

    def get_access_token(self, code):
        client = httplib2.Http()
        params = {'client_id': self.consumer_key,
                  'redirect_uri': self.callback_url,
                  'grant_type': 'authorization_code',
                  'client_secret': self.consumer_secret,
                  'scope': self.scope,
                  'code': code}
        url = self.access_token_url
        # TODO: Proper exception handling
        headers = { 'content-type': 'application/x-www-form-urlencoded' }
        resp, content = client.request(url, 'POST',
                                       body=urllib.urlencode(params),
                                       headers=headers)
        access_token = None
        if resp.status == 200:
            if resp['content-type'] == 'application/json':
                data = json.loads(content)
            else:
                data = dict(urlparse.parse_qsl(content))
            access_token = data.get('access_token')
        if not access_token:
            raise OAuth2Error('Error retrieving access token: %s' % content)
            
        return access_token
