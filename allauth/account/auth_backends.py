from threading import local
from typing import Optional, Tuple

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import AbstractBaseUser

from allauth.account.adapter import get_adapter
from allauth.account.app_settings import LoginMethod

from . import app_settings
from .utils import filter_users_by_email, filter_users_by_username


_stash = local()


class AuthenticationBackend(ModelBackend):
    def authenticate(self, request, **credentials):
        password = credentials.get("password")
        if not password:
            return None

        phone = credentials.get("phone")
        user, did_attempt = self._authenticate_by_phone(phone, password)
        if did_attempt:
            return user

        email = credentials.get("email")
        user, did_attempt = self._authenticate_by_email(email, password)
        if did_attempt:
            return user

        username = credentials.get("username")
        if not username:
            return None
        # Username/email ambiguity: even though allauth will pass along
        # `email` explicitly, other apps may not respect this. For example,
        # when using django-tastypie basic authentication, the login is
        # always passed as `username`.  So let's play nice with other apps
        # and use username as fallback.
        if (
            LoginMethod.USERNAME in app_settings.LOGIN_METHODS
            and LoginMethod.EMAIL in app_settings.LOGIN_METHODS
        ):
            user, _ = self._authenticate_by_email(
                username, password, time_attack_mitigation=False
            )
            if not user:
                user, _ = self._authenticate_by_username(username, password)
            return user

        # Either email, or username, is a login method. Not both.  No need
        # to worry about time attacks.
        user, did_attempt = self._authenticate_by_email(username, password)
        if did_attempt:
            return user

        user, _ = self._authenticate_by_username(username, password)
        return user

    def _authenticate_by_phone(
        self, phone: Optional[str], password: str
    ) -> Tuple[Optional[AbstractBaseUser], bool]:
        if LoginMethod.PHONE not in app_settings.LOGIN_METHODS:
            return (None, False)
        if not phone:
            return (None, False)
        adapter = get_adapter()
        user = adapter.get_user_by_phone(phone)
        if user:
            if self._check_password(user, password):
                return (user, True)
        else:
            get_user_model()().set_password(password)
        return (None, True)

    def _authenticate_by_username(
        self, username: Optional[str], password: str
    ) -> Tuple[Optional[AbstractBaseUser], bool]:
        username_field = app_settings.USER_MODEL_USERNAME_FIELD
        if (
            (LoginMethod.USERNAME not in app_settings.LOGIN_METHODS)
            or (not username_field)
            or not username
        ):
            return (None, False)
        User = get_user_model()
        try:
            # Username query is case insensitive
            user = filter_users_by_username(username).get()
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user.
            User().set_password(password)
        else:
            if self._check_password(user, password):
                return (user, True)
        return (None, True)

    def _authenticate_by_email(
        self, email: Optional[str], password: str, time_attack_mitigation: bool = True
    ) -> Tuple[Optional[AbstractBaseUser], bool]:
        if not email or LoginMethod.EMAIL not in app_settings.LOGIN_METHODS:
            return (None, False)
        users = filter_users_by_email(email, prefer_verified=True)
        if users:
            for user in users:
                if self._check_password(user, password):
                    return (user, True)
        elif time_attack_mitigation:
            get_user_model()().set_password(password)
        return (None, True)

    def _check_password(self, user, password):
        ret = user.check_password(password)
        if ret:
            ret = self.user_can_authenticate(user)
            if not ret:
                self._stash_user(user)
        return ret

    @classmethod
    def _stash_user(cls, user):
        """Now, be aware, the following is quite ugly, let me explain:

        Even if the user credentials match, the authentication can fail because
        Django's default ModelBackend calls user_can_authenticate(), which
        checks `is_active`. Now, earlier versions of allauth did not do this
        and simply returned the user as authenticated, even in case of
        `is_active=False`. For allauth scope, this does not pose a problem, as
        these users are properly redirected to an account inactive page.

        This does pose a problem when the allauth backend is used in a
        different context where allauth is not responsible for the login. Then,
        by not checking on `user_can_authenticate()` users will allow to become
        authenticated whereas according to Django logic this should not be
        allowed.

        In order to preserve the allauth behavior while respecting Django's
        logic, we stash a user for which the password check succeeded but
        `user_can_authenticate()` failed. In the allauth authentication logic,
        we can then unstash this user and proceed pointing the user to the
        account inactive page.
        """
        global _stash
        ret = getattr(_stash, "user", None)
        _stash.user = user
        return ret

    @classmethod
    def unstash_authenticated_user(cls):
        return cls._stash_user(None)
