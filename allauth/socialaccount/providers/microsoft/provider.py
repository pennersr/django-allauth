from __future__ import unicode_literals

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class MicrosoftGraphAccount(ProviderAccount):
    def to_str(self):
        name = self.account.extra_data.get("displayName")
        if name and name.strip() != "":
            return name
        return super(MicrosoftGraphAccount, self).to_str()


class MicrosoftGraphProvider(OAuth2Provider):
    id = str("microsoft")
    name = "Microsoft Graph"
    account_class = MicrosoftGraphAccount

    def get_default_scope(self):
        """
        Doc on scopes available at
        https://developer.microsoft.com/en-us/graph/docs/concepts/permissions_reference
        """
        return ["User.Read"]

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        email = data.get("mail") or data.get("userPrincipalName")
        return dict(
            email=email,
            last_name=data.get("surname"),
            first_name=data.get("givenName"),
        )


provider_classes = [MicrosoftGraphProvider]
