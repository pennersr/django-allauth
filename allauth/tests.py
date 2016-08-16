# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests
from datetime import datetime, date
from importlib import import_module

import django
from django.conf import settings
from django.test import TestCase as DjangoTestCase
from django.db import models

from allauth.account.utils import user_username
from . import utils
from .compat import urlparse, urlunparse

try:
    from mock import Mock, patch
except ImportError:
    from unittest.mock import Mock, patch  # noqa


class TestCase(DjangoTestCase):

    def setUp(self):
        if django.VERSION < (1, 8,):
            engine = import_module(settings.SESSION_ENGINE)
            s = engine.SessionStore()
            s.save()
            self.client.cookies[
                settings.SESSION_COOKIE_NAME] = s.session_key

    def assertRedirects(self, response, expected_url,
                        fetch_redirect_response=True,
                        **kwargs):
        if django.VERSION >= (1, 7,):
            super(TestCase, self).assertRedirects(
                response,
                expected_url,
                fetch_redirect_response=fetch_redirect_response,
                **kwargs)

        elif fetch_redirect_response:
            super(TestCase, self).assertRedirects(
                response,
                expected_url,
                **kwargs)
        else:
            self.assertEqual(302, response.status_code)
            actual_url = response['location']
            if expected_url[0] == '/':
                parts = list(urlparse(actual_url))
                parts[0] = parts[1] = ''
                actual_url = urlunparse(parts)
            self.assertEqual(expected_url, actual_url)

    def client_force_login(self, user):
        if django.VERSION >= (1, 9):
            self.client.force_login(
                user,
                'django.contrib.auth.backends.ModelBackend')
        else:
            old_password = user.password
            user.set_password('doe')
            user.save()
            self.client.login(
                username=user_username(user),
                password='doe')
            user.password = old_password
            user.save()


class MockedResponse(object):
    def __init__(self, status_code, content, headers=None):
        if headers is None:
            headers = {}

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
        self.orig_request = requests.request

        def mockable_request(f):
            def new_f(*args, **kwargs):
                if self.responses:
                    return self.responses.pop(0)
                return f(*args, **kwargs)
            return new_f
        requests.get = mockable_request(requests.get)
        requests.post = mockable_request(requests.post)
        requests.request = mockable_request(requests.request)

    def __exit__(self, type, value, traceback):
        requests.get = self.orig_get
        requests.post = self.orig_post
        requests.request = self.orig_request


class BasicTests(TestCase):

    def test_generate_unique_username(self):
        examples = [('a.b-c@gmail.com', 'a.b-c'),
                    ('Üsêrnamê', 'username'),
                    ('User Name', 'user_name'),
                    ('', 'user')]
        for input, username in examples:
            self.assertEqual(utils.generate_unique_username([input]),
                             username)

    def test_email_validation(self):
        is_email_max_75 = django.VERSION[:2] <= (1, 7)
        if is_email_max_75:
            s = 'unfortunately.django.user.email.max_length.is.set.to.75.which.is.too.short@bummer.com'  # noqa
            self.assertEqual(None, utils.valid_email_or_none(s))
        s = 'this.email.address.is.a.bit.too.long.but.should.still.validate.ok@short.com'  # noqa
        self.assertEqual(s, utils.valid_email_or_none(s))
        if is_email_max_75:
            s = 'x' + s
            self.assertEqual(None, utils.valid_email_or_none(s))
            self.assertEqual(None, utils.valid_email_or_none("Bad ?"))

    def test_serializer(self):
        class SomeModel(models.Model):
            dt = models.DateTimeField()
            t = models.TimeField()
            d = models.DateField()

        def method(self):
            pass

        instance = SomeModel(dt=datetime.now(),
                             d=date.today(),
                             t=datetime.now().time())
        # make sure serializer doesn't fail if a method is attached to
        # the instance
        instance.method = method
        instance.nonfield = 'hello'
        data = utils.serialize_instance(instance)
        instance2 = utils.deserialize_instance(SomeModel, data)
        self.assertEqual(getattr(instance, 'method', None), method)
        self.assertEqual(getattr(instance2, 'method', None), None)
        self.assertEqual(instance.nonfield, instance2.nonfield)
        self.assertEqual(instance.d, instance2.d)
        self.assertEqual(instance.dt.date(), instance2.dt.date())
        for t1, t2 in [(instance.t, instance2.t),
                       (instance.dt.time(), instance2.dt.time())]:
            self.assertEqual(t1.hour, t2.hour)
            self.assertEqual(t1.minute, t2.minute)
            self.assertEqual(t1.second, t2.second)
            # AssertionError: datetime.time(10, 6, 28, 705776)
            #     != datetime.time(10, 6, 28, 705000)
            self.assertEqual(int(t1.microsecond / 1000),
                             int(t2.microsecond / 1000))

    def test_serializer_binary_field(self):
        class SomeBinaryModel(models.Model):
            bb = models.BinaryField()
            bb_empty = models.BinaryField()

        instance = SomeBinaryModel(bb=b'some binary data')

        serialized = utils.serialize_instance(instance)
        deserialized = utils.deserialize_instance(SomeBinaryModel, serialized)

        self.assertEqual(serialized['bb'], 'c29tZSBiaW5hcnkgZGF0YQ==')
        self.assertEqual(serialized['bb_empty'], '')
        self.assertEqual(deserialized.bb, b'some binary data')
        self.assertEqual(deserialized.bb_empty, b'')

    def test_build_absolute_uri(self):
        self.assertEqual(
            utils.build_absolute_uri(None, '/foo'),
            'http://example.com/foo')
        self.assertEqual(
            utils.build_absolute_uri(None, '/foo', protocol='ftp'),
            'ftp://example.com/foo')
        self.assertEqual(
            utils.build_absolute_uri(None, 'http://foo.com/bar'),
            'http://foo.com/bar')
