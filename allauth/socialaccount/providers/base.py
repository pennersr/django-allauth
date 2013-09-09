from django.utils.encoding import python_2_unicode_compatible

from allauth.socialaccount import app_settings

from ..models import SocialApp, SocialAccount, SocialLogin
from ..adapter import get_adapter


class AuthProcess(object):
    LOGIN = 'login'
    CONNECT = 'connect'


class AuthAction(object):
    AUTHENTICATE = 'authenticate'
    REAUTHENTICATE = 'reauthenticate'


class Provider(object):
    def get_login_url(self, request, next=None, **kwargs):
        """
        Builds the URL to redirect to when initiating a login for this
        provider.
        """
        raise NotImplementedError("get_login_url() for " + self.name)

    def get_app(self, request):
        return SocialApp.objects.get_current(self.id)

    def media_js(self, request):
        """
        Some providers may require extra scripts (e.g. a Facebook connect)
        """
        return ''

    def wrap_account(self, social_account):
        return self.account_class(social_account)

    def get_settings(self):
        return app_settings.PROVIDERS.get(self.id, {})

    def sociallogin_from_response(self, request, response):
        adapter = get_adapter()
        uid = self.extract_uid(response)
        extra_data = self.extract_extra_data(response)
        common_fields = self.extract_common_fields(response)
        socialaccount = SocialAccount(extra_data=extra_data,
                                      uid=uid,
                                      provider=self.id)
        email_addresses = self.extract_email_addresses(response)
        sociallogin = SocialLogin(socialaccount,
                                  email_addresses=email_addresses)
        user = socialaccount.user = adapter.new_user(request, sociallogin)
        user.set_unusable_password()
        adapter.populate_user(request, sociallogin, common_fields)
        return sociallogin

    def extract_extra_data(self, data):
        return data

    def extract_basic_socialaccount_data(self, data):
        """
        Returns a tuple of basic/common social account data.
        For example: ('123', {'first_name': 'John'})
        """
        raise NotImplementedError

    def extract_common_fields(self, data):
        """
        For example:

        {'first_name': 'John'}
        """
        return {}

    def extract_email_addresses(self, data):
        """
        For example:

        [EmailAddress(email='john@doe.org',
                      verified=True,
                      primary=True)]
        """
        return []


@python_2_unicode_compatible
class ProviderAccount(object):
    def __init__(self, social_account):
        self.account = social_account

    def get_profile_url(self):
        return None

    def get_avatar_url(self):
        return None

    def get_brand(self):
        """
        Returns a dict containing an id and name identifying the
        brand. Useful when displaying logos next to accounts in
        templates.

        For most providers, these are identical to the provider. For
        OpenID however, the brand can derived from the OpenID identity
        url.
        """
        provider = self.account.get_provider()
        return dict(id=provider.id,
                    name=provider.name)

    def __str__(self):
        return self.to_str()

    def to_str(self):
        """
        Due to the way python_2_unicode_compatible works, this does not work:

            @python_2_unicode_compatible
            class GoogleAccount(ProviderAccount):
                def __str__(self):
                    dflt = super(GoogleAccount, self).__str__()
                    return self.account.extra_data.get('name', dflt)

        It will result in and infinite recursion loop. That's why we
        add a method `to_str` that can be overriden in a conventional
        fashion, without having to worry about @python_2_unicode_compatible
        """
        return self.get_brand()['name']
