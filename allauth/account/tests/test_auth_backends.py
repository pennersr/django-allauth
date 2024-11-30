from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test.utils import override_settings

import pytest

from allauth.account import app_settings
from allauth.account.auth_backends import AuthenticationBackend
from allauth.tests import TestCase


class AuthenticationBackendTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create(
            is_active=True, email="john@example.com", username="john"
        )
        user.set_password(user.username)
        user.save()
        self.user = user

    @override_settings(
        ACCOUNT_AUTHENTICATION_METHOD=app_settings.AuthenticationMethod.USERNAME
    )  # noqa
    def test_auth_by_username(self):
        user = self.user
        backend = AuthenticationBackend()
        self.assertEqual(
            backend.authenticate(
                request=None, username=user.username, password=user.username
            ).pk,
            user.pk,
        )
        self.assertEqual(
            backend.authenticate(
                request=None, username=user.email, password=user.username
            ),
            None,
        )

    @override_settings(
        ACCOUNT_AUTHENTICATION_METHOD=app_settings.AuthenticationMethod.EMAIL
    )  # noqa
    def test_auth_by_email(self):
        user = self.user
        backend = AuthenticationBackend()
        self.assertEqual(
            backend.authenticate(
                request=None, username=user.email, password=user.username
            ).pk,
            user.pk,
        )
        self.assertEqual(
            backend.authenticate(
                request=None, username=user.username, password=user.username
            ),
            None,
        )

    @override_settings(
        ACCOUNT_AUTHENTICATION_METHOD=app_settings.AuthenticationMethod.USERNAME_EMAIL
    )  # noqa
    def test_auth_by_username_or_email(self):
        user = self.user
        backend = AuthenticationBackend()
        self.assertEqual(
            backend.authenticate(
                request=None, username=user.email, password=user.username
            ).pk,
            user.pk,
        )
        self.assertEqual(
            backend.authenticate(
                request=None, username=user.username, password=user.username
            ).pk,
            user.pk,
        )


@pytest.mark.parametrize(
    "auth_method",
    [
        app_settings.AuthenticationMethod.EMAIL,
        app_settings.AuthenticationMethod.USERNAME,
        app_settings.AuthenticationMethod.USERNAME_EMAIL,
    ],
)
def test_account_enumeration_timing_attack(user, db, rf, settings, auth_method):
    settings.ACCOUNT_AUTHENTICATION_METHOD = auth_method
    with patch("django.contrib.auth.models.User.set_password") as set_password_mock:
        with patch(
            "django.contrib.auth.models.User.check_password", new=set_password_mock
        ):
            backend = AuthenticationBackend()
            backend.authenticate(
                rf.get("/"),
                email="not@known.org",
                username="not-known",
                password="secret",
            )
            set_password_mock.assert_called_once()
            set_password_mock.reset_mock()
            backend.authenticate(rf.get("/"), username=user.username, password="secret")
            set_password_mock.assert_called_once()
            set_password_mock.reset_mock()
            backend.authenticate(
                rf.get("/"), email=user.email, username="not-known", password="secret"
            )
            set_password_mock.assert_called_once()
