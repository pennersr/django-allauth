from allauth.account.models import EmailAddress
from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.wahoo.views import WahooOAuth2Adapter


class WahooAccount(ProviderAccount):
    def get_profile_url(self):
        return "https://api.wahooligan.com/v1/user"


class WahooProvider(OAuth2Provider):
    id = "wahoo"
    name = "Wahoo"
    account_class = WahooAccount
    oauth2_adapter_class = WahooOAuth2Adapter

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        extra_common = super(WahooProvider, self).extract_common_fields(data)
        extra_common.update(
            # Additional properties we ignore: gender, created_at, updated_at
            height=data.get("height"),
            weight=data.get("weight"),
            first=data.get("first"),
            last=data.get("last"),
            birth=data.get("birth"),
        )
        return extra_common

    def extract_email_addresses(self, data):
        email = EmailAddress(
            email=data.get("email"),
            primary=True,
            verified=False,
        )
        return [email]

    def get_default_scope(self):
        scope = ["user_read"]
        if app_settings.QUERY_EMAIL:
            scope.append("email")
        return scope


provider_classes = [WahooProvider]
