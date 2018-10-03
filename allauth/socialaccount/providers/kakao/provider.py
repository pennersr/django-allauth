from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class KakaoAccount(ProviderAccount):
    @property
    def properties(self):
        return self.account.extra_data['properties']

    def get_avatar_url(self):
        return self.properties['profile_image']

    def to_str(self):
        dflt = super(KakaoAccount, self).to_str()
        return self.properties['nickname'] or dflt


class KakaoProvider(OAuth2Provider):
    id = 'kakao'
    name = 'Kakao'
    account_class = KakaoAccount

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        email = data.get("kaccount_email")
        return dict(email=email)

    def extract_email_addresses(self, data):
        ret = []
        email = data.get("kaccount_email")
        if email:
            verified = data.get("kaccount_email_verified")
            # data["kaccount_email_verified"] imply the email address is
            # verified
            ret.append(EmailAddress(email=email,
                                    verified=verified,
                                    primary=True))
        return ret


provider_classes = [KakaoProvider]
