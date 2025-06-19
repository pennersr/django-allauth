from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.utils import override_settings

import pytest

from allauth.account import app_settings
from allauth.account.auth_backends import AuthenticationBackend


class AuthenticationBackendTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create(
            is_active=True, email="john@example.com", username="john"
        )
        user.set_password(user.username)
        user.save()
        self.user = user

    @override_settings(
        ACCOUNT_LOGIN_METHODS={app_settings.LoginMethod.USERNAME}
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

    @override_settings(ACCOUNT_LOGIN_METHODS={app_settings.LoginMethod.EMAIL})  # noqa
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
        ACCOUNT_LOGIN_METHODS={
            app_settings.LoginMethod.EMAIL,
            app_settings.LoginMethod.USERNAME,
        }
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
    "login_methods",
    [
        {app_settings.LoginMethod.EMAIL},
        {app_settings.LoginMethod.USERNAME},
        {app_settings.LoginMethod.USERNAME, app_settings.LoginMethod.EMAIL},
    ],
)
def test_account_enumeration_timing_attack(user, db, rf, settings, login_methods):
    settings.ACCOUNT_LOGIN_METHODS = login_methods
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
