from __future__ import unicode_literals

from allauth.socialaccount.providers.base import AuthAction, ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class MicrosoftGraphAccount(ProviderAccount):
    def get_avatar_url(self):
        return self.account.extra_data.get("photo")

    def to_str(self):
        dflt = super(MicrosoftGraphAccount, self).to_str()
        return self.account.extra_data.get("displayName", dflt)


class MicrosoftGraphProvider(OAuth2Provider):
    id = str("microsoft")
    name = "Microsoft Graph"
    account_class = MicrosoftGraphAccount

    def get_default_scope(self):
        """
        Docs on Scopes and Permissions:
        https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-permissions-and-consent#scopes-and-permissions
        """
        return ["User.Read"]

    def get_auth_params(self, request, action):
        ret = super(MicrosoftGraphProvider, self).get_auth_params(request, action)
        if action == AuthAction.REAUTHENTICATE:
            ret["prompt"] = "select_account"
        return ret

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        return dict(
            email=data.get("mail") or data.get("userPrincipalName"),
            username=data.get("mailNickname"),
            last_name=data.get("surname"),
            first_name=data.get("givenName"),
        )


provider_classes = [MicrosoftGraphProvider]
