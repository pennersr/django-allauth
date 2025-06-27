import json
import requests
from unittest.mock import Mock


class MockedResponse:
    def __init__(self, status_code, content, headers=None):
        if headers is None:
            headers = {}

        self.status_code = status_code
        if isinstance(content, dict):
            content = json.dumps(content)
            headers["content-type"] = "application/json"
        self.content = content.encode("utf8")
        self.headers = headers

    def json(self):
        return json.loads(self.text)

    def raise_for_status(self):
        pass

    @property
    def ok(self):
        return self.status_code // 100 == 2

    @property
    def text(self):
        return self.content.decode("utf8")


class mocked_response:
    def __init__(self, *responses, callback=None):
        self.callback = callback
        self.responses = list(responses)

    def __enter__(self):
        self.orig_get = requests.Session.get
        self.orig_post = requests.Session.post
        self.orig_request = requests.Session.request

        def mockable_request(f):
            def new_f(*args, **kwargs):
                if self.callback:
                    response = self.callback(*args, **kwargs)
                    if response is not None:
                        return response
                if self.responses:
                    resp = self.responses.pop(0)
                    if isinstance(resp, dict):
                        resp = MockedResponse(200, resp)
                    return resp
                return f(*args, **kwargs)

            return Mock(side_effect=new_f)

        requests.Session.get = mockable_request(requests.Session.get)
        requests.Session.post = mockable_request(requests.Session.post)
        requests.Session.request = mockable_request(requests.Session.request)

    def __exit__(self, type, value, traceback):
        requests.Session.get = self.orig_get
        requests.Session.post = self.orig_post
        requests.Session.request = self.orig_request
