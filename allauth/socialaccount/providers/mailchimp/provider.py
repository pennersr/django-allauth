"""Customise Provider classes for MailChimp API v3."""
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class MailChimpAccount(ProviderAccount):

    """ProviderAccount subclass for MailChimp."""

    def get_profile_url(self):
        """Return base profile url."""
        return self.account.extra_data['api_endpoint']

    def get_avatar_url(self):
        """Return avatar url."""
        return self.account.extra_data['login']['avatar']


class MailChimpProvider(OAuth2Provider):

    """OAuth2Provider subclass for MailChimp v3."""

    id = 'mailchimp'
    name = 'MailChimp'
    account_class = MailChimpAccount

    def extract_uid(self, data):
        """Extract uid ('user_id') and ensure it's a str."""
        return str(data['user_id'])

    def get_default_scope(self):
        """Ensure scope is null to fit their API."""
        return ['']

    def extract_common_fields(self, data):
        """Extract fields from a metadata query."""
        return dict(
            dc=data.get('dc'),
            role=data.get('role'),
            account_name=data.get('accountname'),
            user_id=data.get('user_id'),
            login=data.get('login'),
            login_url=data.get('login_url'),
            api_endpoint=data.get('api_endpoint'),
        )


provider_classes = [MailChimpProvider]
