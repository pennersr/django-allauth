from django.conf import settings

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q

import app_settings

class AuthenticationBackend(ModelBackend):
    
    def authenticate(self, **credentials):
        ret = None
        if not app_settings.ACCOUNT_AUTHENTICATION == app_settings.USERNAME:
            # Also handle 'username' as e-mail to play nice
            # with other apps (e.g. django-tastypie basic authentication)
            email = credentials.get('email')
            if email:
                users = User.objects.filter(Q(email__iexact=email)
                                            | Q(emailaddress__email__iexact
                                                =email))
                for user in users:
                    if user.check_password(credentials["password"]):
                        return user
        ret = super(AuthenticationBackend, self).authenticate(**credentials)
        return ret


