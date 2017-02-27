"""Customise Provider classes for Eventbrite API v3."""
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class EventbriteAccount(ProviderAccount):

    """ProviderAccount subclass for Eventbrite."""

    def get_avatar_url(self):
        """Return avatar url."""
        return self.account.extra_data['image_id']


class EventbriteProvider(OAuth2Provider):

    """OAuth2Provider subclass for Eventbrite."""

    id = 'eventbrite'
    name = 'Eventbrite'
    account_class = EventbriteAccount

    def extract_uid(self, data):
        """Extract uid ('id') and ensure it's a str."""
        return str(data['id'])

    def get_default_scope(self):
        """Ensure scope is null to fit their API."""
        return ['']

    def extract_common_fields(self, data):
        """Extract fields from a basic user query."""
        return dict(
            emails=data.get('emails'),
            id=data.get('id'),
            name=data.get('name'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            image_url=data.get('image_url')
        )


provider_classes = [EventbriteProvider]
