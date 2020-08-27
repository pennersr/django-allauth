from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class ZohoAccount(ProviderAccount):

    def to_str(self):
        dflt = super(ZohoAccount, self).to_str()
        return self.account.extra_data.get('Display_Name', dflt)


class ZohoProvider(OAuth2Provider):
    id = 'zoho'
    name = 'Zoho'
    account_class = ZohoAccount

    def get_default_scope(self):
        return ['aaaserver.profile.READ']

    def extract_uid(self, data):
        return data['ZUID']

    def extract_common_fields(self, data):
        return dict(
            email=data['Email'],
            username=data['Display_Name'],
            first_name=data['First_Name'],
            last_name=data['Last_Name'],
        )

    def extract_email_addresses(self, data):
        ret = []
        email = data.get('Email')
        if email:
            ret.append(EmailAddress(
                email=email,
                verified=False,
                primary=True,
            ))
        return ret


provider_classes = [ZohoProvider]
