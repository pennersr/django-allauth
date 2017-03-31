"""Customise Provider classes for Eventbrite API v3."""
from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider

API_URL = 'https://www.eventbriteapi.com/v3/'


class EventbriteAccount(ProviderAccount):

    """ProviderAccount subclass for Eventbrite."""

    def get_profile_url(self):
        """
        Return a URL for a user profile irrespective of their login status.

        NB: This URL by itself will not provide access. It must be
        combined with the user's token either via ?token=user's_token (where
        user's_token is their token string) or via the following example:

        >>> import requests
        >>> headers = {'Authorization': 'Bearer {0}'.format("user's_token")}
        >>> profile_url = API_URL + 'users/' + self.account.extra_data['id']
        >>> profile = requests.get(profile_url).json()
        """
        return API_URL + 'users/' + self.account.extra_data['id']

    def get_avatar_url(self):
        """
        Return avatar data endpoint.

        NB: This doesn't currently return a image file URL, but an endpoint for
        the user's avatar data. The actual image url can be queried from this
        endpoint via the 'url' key, but the user's Eventbrite token must either
        be included in the header or in the url itself.

        >>> import requests
        >>> headers = {'Authorization': 'Bearer {0}'.format("user's_token")}
        >>> image_url_endpoint = (API_URL + 'media/' +
        ...                       self.account.extra_data['image_id'])
        >>> response = requests.get(image_url_endpoint)
        >>> url = response.json()['url']
        """
        return API_URL + 'media/' + self.account.extra_data['image_id']

    def to_str(self):
        """A wrapper method for __str__ for python 2 compatibility."""
        dflt = super(EventbriteAccount, self).to_str()
        return self.account.extra_data.get('name', dflt)


class EventbriteProvider(OAuth2Provider):

    """OAuth2Provider subclass for Eventbrite."""

    id = 'eventbrite'
    name = 'Eventbrite'
    account_class = EventbriteAccount

    def extract_uid(self, data):
        """Extract uid ('id') and ensure it's a str."""
        return str(data['id'])

    def extract_common_fields(self, data):
        """Extract fields from a default query of v3/users/me"""
        return dict(
            emails=data.get('emails'),
            id=data.get('id'),
            name=data.get('name'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            image_id=data.get('image_id')
        )

    def extract_email_addresses(self, data):
        """Extract email addresses if verified."""
        ret = []
        emails = data.get('emails')
        for email in emails:
            ret.append(EmailAddress(email=email['email'],
                                    verified=email['verified'],
                                    primary=email['primary']))
        return ret


provider_classes = [EventbriteProvider]
