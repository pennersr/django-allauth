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
                 access_token_method,
                 access_token_url,
                 callback_url,
                 scope):
        self.request = request
        self.access_token_method = access_token_method
        self.access_token_url = access_token_url
        self.callback_url = callback_url
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.scope = ' '.join(scope)
        self.state = None
        self.custom_header = None
        self.scope_delimiter = ' '
        self.use_http_auth = False

    def get_redirect_url(self, authorization_url, extra_params):
        params = {
            'client_id': self.consumer_key,
            'redirect_uri': self.callback_url,
            'scope': self.scope,
            'response_type': 'code'
        }
        if self.state:
            params['state'] = self.state
        params.update(extra_params)
        return '%s?%s' % (authorization_url, urlencode(params))

    def get_access_token(self, code):
        if self.custom_header is not None:
            headers = self.custom_header
        data = {'client_id': self.consumer_key,
                'redirect_uri': self.callback_url,
                'grant_type': 'authorization_code',
                'client_secret': self.consumer_secret,
                'code': code}
        params = None
        self._strip_empty_keys(data)
        url = self.access_token_url
        if self.access_token_method == 'GET':
            params = data
            data = None
        # TODO: Proper exception handling
        
        # If we are sending clientID and client secret as parameters, rather
        # than using HTTP basic auth
        if self.use_http_auth == False:
            # No custom header sent
            if self.custom_header is None:
                resp = requests.request(self.access_token_method,
                                url,
                                params=params,
                                data=data)
            # Custom header is set    
            if self.custom_header is not None:
                resp = requests.request(self.access_token_method,
                                url,
                                params=params,
                                data=data,
                                headers = self.custom_header)
         
        # If we are using HTTP basic auth to send client ID and secret 
        if self.use_http_auth == True:
            post_data = {"grant_type": "authorization_code",
                 "code": code,
                 "redirect_uri": self.callback_url}
            client_auth = requests.auth.HTTPBasicAuth(self.consumer_key,self.consumer_secret)
            # No custom header set
            if self.custom_header is None:
                resp = requests.post(url,
                 auth=client_auth,
                 data=post_data)
            # Custom header is set    
            if self.custom_header is not None: 
                resp = requests.post(url,
                 auth=client_auth,
                 data=post_data,
                 headers=headers)   
                            
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

    def _strip_empty_keys(self, params):
        """Added because the Dropbox OAuth2 flow doesn't 
        work when scope is passed in, which is empty.
        """
        keys = [k for k, v in params.items() if v == '']
        for key in keys:
            del params[key]
     
    # Set custom header for requesting access token
    # Needed by Reddit        
    def set_custom_header(self, custom_header):
         self.custom_header = custom_header
     
    # Set delimiter for scope (default is space) 
    # Not necessary for Reddit, but was mentioned in another issue
    def set_scope_delimiter(self, scope_delimiter):
        # Adjust scope variable
         self.scope = self.scope.replace(self.scope_delimiter, scope_delimiter)
         self.scope_delimiter = scope_delimiter
         
    # Client should use HTTP basic auth for client ID and secret 
    # rather then sending them as parameters 
    # Required by Reddit   
    def set_http_auth(self,use_http_auth):
        self.use_http_auth = use_http_auth           
