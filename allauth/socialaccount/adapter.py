from django.core.urlresolvers import reverse

from ..utils import (import_attribute,
                     get_user_model,
                     valid_email_or_none)
from ..account.utils import user_email, user_username

from . import app_settings

class DefaultSocialAccountAdapter(object):
    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a
        social provider, but before the login is actually processed
        (and before the pre_social_login signal is emitted).

        You can use this hook to intervene, e.g. abort the login by
        raising an ImmediateHttpResponse
        
        Why both an adapter hook and the signal? Intervening in
        e.g. the flow from within a signal handler is bad -- multiple
        handlers may be active and are executed in undetermined order.
        """
        pass


    def populate_new_user(self,
                          username=None,
                          first_name=None, 
                          last_name=None,
                          email=None,
                          name=None):
        """
        Spawns a new User instance, safely and leniently populating
        several common fields. 

        This method is used to create a suggested User instance that
        represents the social user that is in the process of being
        logged in. Validation is not a requirement. For example,
        verifying whether or not a username already exists, is not a
        responsibility.
        """
        user = get_user_model()()
        user_username(user, username or '')
        user_email(user, valid_email_or_none(email) or '')
        name_parts= (name or '').partition(' ')
        user.first_name = first_name or name_parts[0]
        user.last_name = last_name or name_parts[2]
        return user

    def get_connect_redirect_url(self, request, socialaccount):
        """
        Returns the default URL to redirect to after successfully
        connecting a social account.
        """
        assert request.user.is_authenticated()
        url = reverse('socialaccount_connections')
        return url


def get_adapter():
    return import_attribute(app_settings.ADAPTER)()

