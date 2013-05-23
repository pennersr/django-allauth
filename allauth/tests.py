# -*- coding: utf-8 -*-

import requests
from django.test import TestCase

from . import utils

class MockedResponse(object):
    def __init__(self, status_code, content, headers={}):
        self.status_code = status_code
        self.content = content
        self.headers = headers

    def json(self):
        import json
        return json.loads(self.content)

    @property
    def text(self):
        return self.content

class mocked_response:
    def __init__(self, *responses):
        self.responses = list(responses)

    def __enter__(self):
        self.orig_get = requests.get
        self.orig_post = requests.post

        def mockable_request(f):
            def new_f(*args, **kwargs):
                if self.responses:
                    return self.responses.pop(0)
                return f(*args, **kwargs)
            return new_f
        requests.get = mockable_request(requests.get)
        requests.post = mockable_request(requests.post)

    def __exit__(self, type, value, traceback):
        requests.get = self.orig_get
        requests.post = self.orig_post

class BasicTests(TestCase):

    def test_generate_unique_username(self):
        examples = [('a.b-c@gmail.com', 'a.b-c'),
                    (u'Üsêrnamê', 'username'),
                    ('', 'user')]
        for input, username in examples:
            self.assertEqual(utils.generate_unique_username(input),
                              username)

    def test_email_validation(self):
        s = 'unfortunately.django.user.email.max_length.is.set.to.75.which.is.too.short@bummer.com'
        self.assertEqual(None, utils.valid_email_or_none(s))
        s = 'this.email.address.is.a.bit.too.long.but.should.still.validate.ok@short.com'
        self.assertEqual(s, utils.valid_email_or_none(s))
        s = 'x' + s
        self.assertEqual(None, utils.valid_email_or_none(s))
        self.assertEqual(None, utils.valid_email_or_none("Bad ?"))
