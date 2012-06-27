from allauth.socialaccount import app_settings
from allauth.socialaccount.models import SocialApp

class Provider(object):
    def get_login_url(self, request, next=None, **kwargs):
        """
        Builds the URL to redirect to when initiating a login for this
        provider. 
        """
        raise NotImplementedError, "get_login_url() for " + self.name

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

    def __unicode__(self):
        return self.get_brand()['name']
