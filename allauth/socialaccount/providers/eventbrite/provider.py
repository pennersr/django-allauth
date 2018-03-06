"""Customise Provider classes for Eventbrite API v3."""
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.account.models import EmailAddress


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
        emails = data.get('emails', [])
        if emails:
            emails = [(int(e['primary']), int(e['verified']), e['email']) for e in emails]
            emails.sort(reverse=True)
            email = emails[0][-1]
        else:
            email = None
        return dict(
            email=email,
            id=data.get('id'),
            name=data.get('name'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            image_url=data.get('image_url')
        )

    def extract_email_addresses(self, data):
        ret = []
        email = data.get('emails')
        for email_data in data.get('emails'):
            ret.append(EmailAddress(email=email_data['email'],
                       verified=email_data['verified'],
                       primary=email_data['primary']))
        return ret



provider_classes = [EventbriteProvider]
