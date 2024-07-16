from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.zoom.views import ZoomOAuth2Adapter


class ZoomAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get("vanity_url")

    def get_avatar_url(self):
        return self.account.extra_data.get("pic_url")


class ZoomProvider(OAuth2Provider):
    id = "zoom"
    name = "Zoom"
    account_class = ZoomAccount
    oauth2_adapter_class = ZoomOAuth2Adapter

    def extract_uid(self, data):
        return data["id"]

    def extract_common_fields(self, data):
        return dict(
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
        )

    def extract_email_addresses(self, data):
        ret = []
        email = data.get("email")
        if email and data.get("verified"):
            ret.append(EmailAddress(email=email, verified=True, primary=True))
        return ret


provider_classes = [ZoomProvider]
