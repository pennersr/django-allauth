from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class AppleProvider(OAuth2Provider):
    id = 'apple'
    name = 'Apple'

    def extract_uid(self, data):
        return str(data['sub'])
        
    def extract_common_fields(self, data):
        return dict(
            email=data.get('email'),
            username=data.get('username', ''),
            name=((data.get('first_name', '') + ' ' +
                  data.get('last_name', '')).strip()),
        )

    def extract_email_addresses(self, data):
        ret = []
        email = data.get('email')
        if email:
            ret.append(EmailAddress(email=email, verified=data.get('email_verified'), primary=True))
        return ret

provider_classes = [AppleProvider]
