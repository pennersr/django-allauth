from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class AppleProvider(OAuth2Provider):
    id = 'apple'
    name = 'Apple'
    account_class = ProviderAccount

    def extract_uid(self, data):
        return str(data['sub'])

    def extract_common_fields(self, data):
        data = {
            "email": data.get("email")
        }

        user_scope_data = data["user_scope_data"]
        # Apple provide user name in nested json
        # So check whether there is name
        name = user_scope_data.get("name")
        if name:
            data["first_name"] = name.get("firstName", "")
            data["last_name"] = name.get("lastName", "")

        return data

    def extract_email_addresses(self, data):
        ret = []
        email = data.get('email')
        if email:
            ret.append(
                EmailAddress(
                    email=email,
                    verified=data.get('email_verified'),
                    primary=True,
                )
            )
        return ret

    def get_default_scope(self):
        return ["name"]


provider_classes = [AppleProvider]
