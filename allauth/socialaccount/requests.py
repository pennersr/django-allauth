import urllib
import httplib2

class Response(object):
    def __init__(self, resp, content):
        self.content = content
        self.headers = dict(resp.iteritems())
        self.status_code = resp.status

    @property
    def json(self):
        import json
        return json.loads(self.content)

def get(url, params={}):
    client = httplib2.Http()
    query = urllib.urlencode(params)
    if query:
        url += '?' + query
    resp, content = client.request(url, 'GET')
    return Response(resp, content)

def post(url, params):
    client = httplib2.Http()
    headers = { 'content-type': 'application/x-www-form-urlencoded' }
    resp, content = client.request(url, 'POST',
                                   body=urllib.urlencode(params),
                                   headers=headers)
    return Response(resp, content)


