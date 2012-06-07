import urllib
import urlparse
import httplib2


class OAuth2Error(Exception):
    pass


class OAuth2Client(object):

    def __init__(self, request, consumer_key, consumer_secret,
                 authorization_url,
                 access_token_url,
                 callback_url):
        self.request = request
        self.authorization_url = authorization_url
        self.access_token_url = access_token_url
        self.callback_url = callback_url
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.scope = None  # TODO

    def get_redirect_url(self):
        params = {
            'client_id': self.consumer_key,
            'redirect_uri': self.callback_url,
            'scope': self.scope or '',
        }
        return '%s?%s' % (self.authorization_url, urllib.urlencode(params))

    def get_access_token(self, code):
        client = httplib2.Http()
        params = {'client_id': self.consumer_key,
                   'redirect_uri': self.callback_url,
                   'client_secret': self.consumer_secret,
                   'code': code}
        url = self.access_token_url + '?' + urllib.urlencode(params)
        # TODO: Proper exception handling
        resp, content = client.request(url, 'POST')
        data = dict(urlparse.parse_qsl(content))
        access_token = data.get('access_token')
        if not access_token:
            raise OAuth2Error(data.get('error', 'Unable to retrieve OAuth2 access token'))
        return access_token
