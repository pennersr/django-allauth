from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth.provider import OAuthProvider


class EvernoteAccount(ProviderAccount):
    def get_profile_url(self):
        return None

    def get_avatar_url(self):
        return None


class EvernoteProvider(OAuthProvider):
    id = 'evernote'
    name = 'Evernote'
    account_class = EvernoteAccount

    def extract_uid(self, data):
        return str(data['edam_userId'])

    def extract_common_fields(self, data):
        return data


provider_classes = [EvernoteProvider]
