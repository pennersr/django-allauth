from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount, AuthAction
from allauth.socialaccount.providers.oauth.provider import OAuthProvider

from allauth.socialaccount import app_settings


class TumblrAccount(ProviderAccount):
    def get_profile_url_(self):
        return self.account.extra_data.get('public-profile-url')

    def get_avatar_url_(self):
        return self.account.extra_data.get('picture-url')

    def to_str(self):
        dflt = super(TumblrAccount, self).to_str()
        name = self.account.extra_data.get('name', dflt)
        return name


class TumblrProvider(OAuthProvider):
    id = 'tumblr'
    name = 'Tumblr'
    package = 'allauth.socialaccount.providers.tumblr'
    account_class = TumblrAccount
    require_callback_url = False

    def get_default_scope(self):
        scope = []
        return scope

    def extract_uid(self, data):
        return data['name']

    def get_profile_fields(self):
        default_fields = ['name']
        fields = self.get_settings().get('PROFILE_FIELDS', default_fields)
        return fields

    def extract_common_fields(self, data):
        return dict(first_name=data.get('name'),)

providers.registry.register(TumblrProvider)
