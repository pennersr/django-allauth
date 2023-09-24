from __future__ import absolute_import

import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.test.utils import override_settings
from django.urls import reverse

from allauth.account import app_settings
from allauth.tests import TestCase


class AjaxTests(TestCase):
    def _send_post_request(self, **kwargs):
        return self.client.post(
            reverse("account_signup"),
            {
                "username": "johndoe",
                "email": "john@example.org",
                "email2": "john@example.org",
                "password1": "johndoe",
                "password2": "johndoe",
            },
            **kwargs,
        )

    def test_no_ajax_header(self):
        resp = self._send_post_request()
        self.assertEqual(302, resp.status_code)
        self.assertRedirects(
            resp, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False
        )

    def test_ajax_header_x_requested_with(self):
        resp = self._send_post_request(HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(200, resp.status_code)
        self.assertEqual(settings.LOGIN_REDIRECT_URL, resp.json()["location"])

    def test_ajax_header_http_accept(self):
        resp = self._send_post_request(HTTP_ACCEPT="application/json")
        self.assertEqual(200, resp.status_code)
        self.assertEqual(settings.LOGIN_REDIRECT_URL, resp.json()["location"])

    def test_ajax_password_reset(self):
        get_user_model().objects.create(
            username="john", email="john@example.org", is_active=True
        )
        resp = self.client.post(
            reverse("account_reset_password"),
            data={"email": "john@example.org"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["john@example.org"])
        self.assertEqual(resp["content-type"], "application/json")

    def test_ajax_login_fail(self):
        resp = self.client.post(
            reverse("account_login"),
            {},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(resp.status_code, 400)
        json.loads(resp.content.decode("utf8"))
        # TODO: Actually test something

    @override_settings(
        ACCOUNT_EMAIL_VERIFICATION=app_settings.EmailVerificationMethod.OPTIONAL
    )
    def test_ajax_login_success(self):
        user = get_user_model().objects.create(username="john", is_active=True)
        user.set_password("doe")
        user.save()
        resp = self.client.post(
            reverse("account_login"),
            {"login": "john", "password": "doe"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content.decode("utf8"))
        self.assertEqual(data["location"], "/accounts/profile/")
