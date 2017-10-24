from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class MeetupAccount(ProviderAccount):
    pass


class MeetupProvider(OAuth2Provider):
    id = 'meetup'
    name = 'Meetup'
    account_class = MeetupAccount

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        return dict(email=data.get('email'),
                    name=data.get('name'))


provider_classes = [MeetupProvider]
