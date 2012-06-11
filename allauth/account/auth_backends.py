from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q

from app_settings import AuthenticationMethod
import app_settings

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
        return super(AuthenticationBackend, self).authenticate(**credentials)

    def _authenticate_by_email(self, **credentials):
        # Even though allauth will pass along `email`, other apps may
        # not respect this setting. For example, when using
        # django-tastypie basic authentication, the login is always
        # passed as `username`.  So let's place nice with other apps
        # and use username as fallback
        email = credentials.get('email', credentials.get('username'))
        if email:
            users = User.objects.filter(Q(email__iexact=email)
                                        | Q(emailaddress__email__iexact
                                            =email))
            for user in users:
                if user.check_password(credentials["password"]):
                    return user
        return None
