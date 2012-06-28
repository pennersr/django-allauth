import urllib
import httplib2

class Response(object):
    def __init__(self, status_code, content, headers={}):
        self.status_code = status_code
        self.content = content
        self.headers = headers

    @classmethod 
    def from_httplib(cls, resp, content):
        return Response(resp.status,
                        content,
                        headers=dict(resp.iteritems()))
    

    @property
    def json(self):
        import json
        return json.loads(self.content)

_mocked_responses = []

def mock_next_request(resp):
    global _mocked_responses
    _mocked_responses.append(resp)

def _mockable_request(f):
    def new_f(*args, **kwargs):
        global _mocked_responses
        if _mocked_responses:
            return _mocked_responses.pop(0)
        return f(*args, **kwargs)
    return new_f
    
@_mockable_request
def get(url, params={}):
    global _mocked_responses
    if _mocked_responses:
        return _mocked_responses.pop(0)
    client = httplib2.Http()
    query = urllib.urlencode(params)
    if query:
        url += '?' + query
    resp, content = client.request(url, 'GET')
    return Response.from_httplib(resp, content)

@_mockable_request
def post(url, params):
    client = httplib2.Http()
    headers = { 'content-type': 'application/x-www-form-urlencoded' }
    resp, content = client.request(url, 'POST',
                                   body=urllib.urlencode(params),
                                   headers=headers)
    return Response.from_httplib(resp, content)


