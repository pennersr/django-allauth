from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class WhaleSpaceAccount(ProviderAccount):
    def get_avatar_url(self):
        return self.account.extra_data.get("profile_image")

    def to_str(self):
        return self.account.extra_data.get("nickname", self.account.uid)


class WhaleSpaceProvider(OAuth2Provider):
    id = "whalespace"
    name = "WhaleSpace"
    account_class = WhaleSpaceAccount

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        email = data.get("email")
        return dict(email=email)

    def extract_email_addresses(self, data):
        ret = []
        email = data.get("email")
        if email:
            ret.append(EmailAddress(email=email, verified=True, primary=True))
        return ret


provider_classes = [WhaleSpaceProvider]