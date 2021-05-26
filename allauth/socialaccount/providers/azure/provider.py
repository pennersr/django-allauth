from __future__ import unicode_literals

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class AzureAccount(ProviderAccount):

    # TODO:
    # - avatar_url:
    #   https://developer.microsoft.com/en-us/graph/docs/api-reference/beta/api/profilephoto_get  # noqa
    def get_username(self):
        return self.account.extra_data["email"]

    def to_str(self):
        name = "{0} {1}".format(
            self.account.extra_data.get("first_name", ""),
            self.account.extra_data.get("last_name", ""),
        )
        if name.strip() != "":
            return name
        return super(AzureAccount, self).to_str()


class AzureProvider(OAuth2Provider):
    id = str("azure")
    name = "Azure"
    account_class = AzureAccount

    def get_default_scope(self):
        """
        Doc on scopes available at
        https://docs.microsoft.com/en-us/azure/active-directory/develop/active-directory-v2-scopes  # noqa
        """
        return ["User.Read", "openid"]

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        email = data.get("mail")
        if not email and "userPrincipalName" in data:
            email = data.get("userPrincipalName")
        return dict(
            email=email,
            username=email,
            last_name=data.get("surname"),
            first_name=data.get("givenName"),
        )


provider_classes = [AzureProvider]
