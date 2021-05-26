from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class CernAccount(ProviderAccount):
    def to_str(self):
        dflt = super(CernAccount, self).to_str()
        return self.account.extra_data.get("name", dflt)


class CernProvider(OAuth2Provider):
    id = "cern"
    name = "Cern"
    account_class = CernAccount

    def get_auth_params(self, request, action):
        data = super(CernProvider, self).get_auth_params(request, action)
        data["scope"] = "read:user"
        return data

    def extract_uid(self, data):
        return str(data.get("id"))

    def extract_common_fields(self, data):
        return dict(
            email=data.get("email"),
            username=data.get("username"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            name=data.get("name"),
        )


provider_classes = [CernProvider]
