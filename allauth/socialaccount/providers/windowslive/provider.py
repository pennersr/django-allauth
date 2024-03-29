from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.windowslive.views import (
    WindowsLiveOAuth2Adapter,
)


class WindowsLiveAccount(ProviderAccount):
    def to_str(self):
        name = "{0} {1}".format(
            self.account.extra_data.get("first_name", ""),
            self.account.extra_data.get("last_name", ""),
        )
        if name.strip() != "":
            return name
        return super(WindowsLiveAccount, self).to_str()


class WindowsLiveProvider(OAuth2Provider):
    id = "windowslive"
    name = "Live"
    account_class = WindowsLiveAccount
    oauth2_adapter_class = WindowsLiveOAuth2Adapter

    def get_default_scope(self):
        """
        Doc on scopes available at
        http://msdn.microsoft.com/en-us/library/dn631845.aspx
        """
        return ["wl.basic", "wl.emails"]

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        try:
            email = data.get("emails").get("preferred")
        except AttributeError:
            email = None

        return dict(
            email=email,
            last_name=data.get("last_name"),
            first_name=data.get("first_name"),
        )


provider_classes = [WindowsLiveProvider]
