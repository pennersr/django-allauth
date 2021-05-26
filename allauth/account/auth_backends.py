from threading import local

from django.contrib.auth.backends import ModelBackend

from ..utils import get_user_model
from . import app_settings
from .app_settings import AuthenticationMethod
from .utils import filter_users_by_email, filter_users_by_username


_stash = local()


class AuthenticationBackend(ModelBackend):
    def authenticate(self, request, **credentials):
        ret = None
        if app_settings.AUTHENTICATION_METHOD == AuthenticationMethod.EMAIL:
            ret = self._authenticate_by_email(**credentials)
        elif app_settings.AUTHENTICATION_METHOD == AuthenticationMethod.USERNAME_EMAIL:
            ret = self._authenticate_by_email(**credentials)
            if not ret:
                ret = self._authenticate_by_username(**credentials)
        else:
            ret = self._authenticate_by_username(**credentials)
        return ret

    def _authenticate_by_username(self, **credentials):
        username_field = app_settings.USER_MODEL_USERNAME_FIELD
        username = credentials.get("username")
        password = credentials.get("password")

        User = get_user_model()

        if not username_field or username is None or password is None:
            return None
        try:
            # Username query is case insensitive
            user = filter_users_by_username(username).get()
            if self._check_password(user, password):
                return user
        except User.DoesNotExist:
            return None

    def _authenticate_by_email(self, **credentials):
        # Even though allauth will pass along `email`, other apps may
        # not respect this setting. For example, when using
        # django-tastypie basic authentication, the login is always
        # passed as `username`.  So let's play nice with other apps
        # and use username as fallback
        email = credentials.get("email", credentials.get("username"))
        if email:
            for user in filter_users_by_email(email):
                if self._check_password(user, credentials["password"]):
                    return user
        return None

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
