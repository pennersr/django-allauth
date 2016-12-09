from django.contrib.auth.backends import ModelBackend

from ..utils import get_user_model
from .utils import (filter_users_by_email,
                    filter_users_by_username)

from .app_settings import AuthenticationMethod
from . import app_settings


class AuthenticationBackend(ModelBackend):

    def authenticate(self, **credentials):
        ret = None
        if app_settings.AUTHENTICATION_METHOD == AuthenticationMethod.EMAIL:
            ret = self._authenticate_by_email(**credentials)
        elif app_settings.AUTHENTICATION_METHOD \
                == AuthenticationMethod.USERNAME_EMAIL:
            ret = self._authenticate_by_email(**credentials)
            if not ret:
                ret = self._authenticate_by_username(**credentials)
        else:
            ret = self._authenticate_by_username(**credentials)
        return ret

    def _authenticate_by_username(self, **credentials):
        username_field = app_settings.USER_MODEL_USERNAME_FIELD
        username = credentials.get('username')
        password = credentials.get('password')

        User = get_user_model()

        if not username_field or username is None or password is None:
            return None
        try:
            # Username query is case insensitive
            user = filter_users_by_username(username).get()
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def _authenticate_by_email(self, **credentials):
        # Even though allauth will pass along `email`, other apps may
        # not respect this setting. For example, when using
        # django-tastypie basic authentication, the login is always
        # passed as `username`.  So let's place nice with other apps
        # and use username as fallback
        email = credentials.get('email', credentials.get('username'))
        if email:
            for user in filter_users_by_email(email):
                if user.check_password(credentials["password"]):
                    return user
        return None
