from threading import local

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

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
        self._did_check_password = False
        user = self._authenticate(request, **credentials)
        if not self._did_check_password:
            self._mitigate_timing_attack(password)
        return user

    def _authenticate(self, request, **credentials):
        password = credentials.get("password")
        username = credentials.get("username")
        if username:
            if LoginMethod.EMAIL in app_settings.LOGIN_METHODS:
                # Username/email ambiguity: even though allauth will pass along
                # `email` explicitly, other apps may not respect this. For example,
                # when using django-tastypie basic authentication, the login is
                # always passed as `username`.  So let's play nice with other apps
                # and use username as fallback.
                user = self._authenticate_by_email(username, password)
                if user:
                    return user
            user = self._authenticate_by_username(username, password)
            if user:
                return user

        email = credentials.get("email")
        if email:
            user = self._authenticate_by_email(email, password)
            if user:
                return user

        phone = credentials.get("phone")
        if phone:
            user = self._authenticate_by_phone(phone, password)
            if user:
                return user
        return None

    def _authenticate_by_phone(self, phone: str, password: str):
        if not phone or LoginMethod.PHONE not in app_settings.LOGIN_METHODS:
            return None
        adapter = get_adapter()
        user = adapter.get_user_by_phone(phone)
        return self._check_password(user, password)

    def _authenticate_by_username(self, username: str, password: str):
        if (
            (LoginMethod.USERNAME not in app_settings.LOGIN_METHODS)
            or (not app_settings.USER_MODEL_USERNAME_FIELD)
            or not username
        ):
            return None
        user = filter_users_by_username(username).first()
        return self._check_password(user, password)

    def _authenticate_by_email(
        self,
        email: str,
        password: str,
    ):
        if not email or LoginMethod.EMAIL not in app_settings.LOGIN_METHODS:
            return None
        users = filter_users_by_email(email, prefer_verified=True)
        for user in users:
            if self._check_password(user, password):
                return user
        return None

    def _mitigate_timing_attack(self, password):
        get_user_model()().set_password(password)

    def _check_password(self, user, password):
        if not user:
            return None
        self._did_check_password = True
        ok = user.check_password(password)
        if ok:
            ok = self.user_can_authenticate(user)
            if not ok:
                self._stash_user(user)
        return user if ok else None

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
