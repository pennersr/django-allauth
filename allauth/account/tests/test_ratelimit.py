from __future__ import absolute_import

from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from django.urls import reverse

from allauth.tests import TestCase


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        },
    },
    ACCOUNT_RATE_LIMITS={"reset_password_email": "1/m"},
)
class RateLimitTests(TestCase):
    def test_case_insensitive_password_reset(self):
        get_user_model().objects.create(email="a@b.com")
        resp = self.client.post(
            reverse("account_reset_password"), data={"email": "a@b.com"}
        )
        assert resp.status_code == 302
        resp = self.client.post(
            reverse("account_reset_password"), data={"email": "A@B.COM"}
        )
        assert resp.status_code == 429
