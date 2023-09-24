from __future__ import absolute_import

import uuid

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.messages.api import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.core import mail, validators
from django.core.exceptions import ValidationError
from django.template import Context, Template
from django.test.client import RequestFactory
from django.test.utils import override_settings

import allauth.app_settings
from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from allauth.account.utils import (
    filter_users_by_username,
    url_str_to_user_pk,
    user_pk_to_url_str,
    user_username,
)
from allauth.core import context
from allauth.tests import TestCase, patch

from .test_models import UUIDUser


test_username_validators = [
    validators.RegexValidator(regex=r"^[a-c]+$", message="not abc", flags=0)
]


class UtilsTests(TestCase):
    def setUp(self):
        self.user_id = uuid.uuid4().hex

    def test_url_str_to_pk_identifies_UUID_as_stringlike(self):
        with patch("allauth.account.utils.get_user_model") as mocked_gum:
            mocked_gum.return_value = UUIDUser
            self.assertEqual(url_str_to_user_pk(self.user_id), uuid.UUID(self.user_id))

    def test_pk_to_url_string_identifies_UUID_as_stringlike(self):
        with patch("allauth.account.utils.get_user_model") as mocked_gum:
            mocked_gum.return_value = UUIDUser
            user = UUIDUser(is_active=True, email="john@example.com", username="john")
            self.assertEqual(user_pk_to_url_str(user), user.pk.hex)

    @override_settings(ACCOUNT_PRESERVE_USERNAME_CASING=False)
    def test_username_lower_cased(self):
        user = get_user_model()()
        user_username(user, "CamelCase")
        self.assertEqual(user_username(user), "camelcase")
        # TODO: Actually test something
        filter_users_by_username("CamelCase", "FooBar")

    @override_settings(ACCOUNT_PRESERVE_USERNAME_CASING=True)
    def test_username_case_preserved(self):
        user = get_user_model()()
        user_username(user, "CamelCase")
        self.assertEqual(user_username(user), "CamelCase")
        # TODO: Actually test something
        filter_users_by_username("camelcase", "foobar")

    def test_user_display(self):
        user = get_user_model()(username="john<br/>doe")
        expected_name = "john&lt;br/&gt;doe"
        templates = [
            "{% load account %}{% user_display user %}",
            "{% load account %}{% user_display user as x %}{{ x }}",
        ]
        for template in templates:
            t = Template(template)
            content = t.render(Context({"user": user}))
            self.assertEqual(content, expected_name)

    def test_message_escaping(self):
        request = RequestFactory().get("/")
        SessionMiddleware(lambda request: None).process_request(request)
        MessageMiddleware(lambda request: None).process_request(request)
        user = get_user_model()()
        user_username(user, "'<8")
        context = {"user": user}
        get_adapter().add_message(
            request, messages.SUCCESS, "account/messages/logged_in.txt", context
        )
        msgs = get_messages(request)
        actual_message = msgs._queued_messages[0].message
        assert user.username in actual_message, actual_message

    def test_email_escaping(self):
        site_name = "testserver"
        if allauth.app_settings.SITES_ENABLED:
            from django.contrib.sites.models import Site

            site = Site.objects.get_current()
            site.name = site_name = '<enc&"test>'
            site.save()
        u = get_user_model().objects.create(username="test", email="user@example.com")
        request = RequestFactory().get("/")
        EmailAddress.objects.add_email(request, u, u.email, confirm=True)
        self.assertTrue(mail.outbox[0].subject[1:].startswith(site_name))

    @override_settings(
        ACCOUNT_USERNAME_VALIDATORS="allauth.account.tests.test_utils.test_username_validators"
    )
    def test_username_validator(self):
        get_adapter().clean_username("abc")
        self.assertRaises(ValidationError, lambda: get_adapter().clean_username("def"))

    @override_settings(ALLOWED_HOSTS=["allowed_host", "testserver"])
    def test_is_safe_url_no_wildcard(self):
        with context.request_context(RequestFactory().get("/")):
            self.assertTrue(get_adapter().is_safe_url("http://allowed_host/"))
            self.assertFalse(get_adapter().is_safe_url("http://other_host/"))

    @override_settings(ALLOWED_HOSTS=["*"])
    def test_is_safe_url_wildcard(self):
        with context.request_context(RequestFactory().get("/")):
            self.assertTrue(get_adapter().is_safe_url("http://foobar.com/"))
            self.assertTrue(get_adapter().is_safe_url("http://other_host/"))

    @override_settings(ALLOWED_HOSTS=["allowed_host", "testserver"])
    def test_is_safe_url_relative_path(self):
        with context.request_context(RequestFactory().get("/")):
            self.assertTrue(get_adapter().is_safe_url("/foo/bar"))
