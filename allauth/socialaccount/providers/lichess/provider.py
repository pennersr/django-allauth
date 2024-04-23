from allauth.socialaccount.providers.lichess.views import LichessOAuth2Adapter
from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider

class LichessAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('url')

    def get_avatar_url(self):
        return self.account.extra_data.get('avatar')

    def to_str(self):
        dflt = super(LichessAccount, self).to_str()
        return self.account.extra_data.get('username', dflt)
    
class LichessProvider(OAuth2Provider):
    id = 'lichess'
    name = 'Lichess'
    account_class = LichessAccount
    oauth2_adapter_class = LichessOAuth2Adapter

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        first_name = data.get('profile', {}).get('firstName')
        last_name = data.get('profile', {}).get('lastName')

        return dict(
            username=data.get('username'), 
            email=data.get('email'), 
            first_name=first_name, 
            last_name=last_name
        )
    
    def extract_email_addresses(self, data):
        ret = []
        email = data.get("email")
        verified = data.get("verified") or False
       
        if email:
            ret.append(
                EmailAddress(
                    email=email,
                    verified=verified,
                    primary=True,
                )
            )
        return ret

    def extract_extra_data(self, data):
        return data
    
provider_classes = [LichessProvider]