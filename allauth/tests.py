# -*- coding: utf-8 -*-

import requests
from datetime import datetime, time, date

from django.test import TestCase
from django.db import models

from . import utils

class MockedResponse(object):
    def __init__(self, status_code, content, headers={}):
        self.status_code = status_code
        self.content = content.encode('utf8')
        self.headers = headers

    def json(self):
        import json
        return json.loads(self.text)

    def raise_for_status(self):
        pass

    @property
    def text(self):
        return self.content.decode('utf8')

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
            self.assertEqual(utils.generate_unique_username([input]),
                              username)

    def test_email_validation(self):
        s = 'unfortunately.django.user.email.max_length.is.set.to.75.which.is.too.short@bummer.com'
        self.assertEqual(None, utils.valid_email_or_none(s))
        s = 'this.email.address.is.a.bit.too.long.but.should.still.validate.ok@short.com'
        self.assertEqual(s, utils.valid_email_or_none(s))
        s = 'x' + s
        self.assertEqual(None, utils.valid_email_or_none(s))
        self.assertEqual(None, utils.valid_email_or_none("Bad ?"))

    def test_serializer(self):
        class SomeModel(models.Model):
            dt = models.DateTimeField()
            t = models.TimeField()
            d = models.DateField()
        instance = SomeModel(dt=datetime.now(),
                             d=date.today(),
                             t=datetime.now().time())
        instance.nonfield = 'hello'
        data = utils.serialize_instance(instance)
        instance2 = utils.deserialize_instance(SomeModel, data)
        self.assertEqual(instance.nonfield, instance2.nonfield)
        self.assertEqual(instance.d, instance2.d)
        self.assertEqual(instance.dt.date(), instance2.dt.date())
        for t1, t2 in [(instance.t, instance2.t),
                       (instance.dt.time(), instance2.dt.time())]:
            self.assertEqual(t1.hour, t2.hour)
            self.assertEqual(t1.minute, t2.minute)
            self.assertEqual(t1.second, t2.second)
            # AssertionError: datetime.time(10, 6, 28, 705776) != datetime.time(10, 6, 28, 705000)
            self.assertEqual(int(t1.microsecond/1000),
                             int(t2.microsecond/1000))
