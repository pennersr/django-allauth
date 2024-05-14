from allauth.account.models import EmailAddress
from allauth.socialaccount.app_settings import QUERY_EMAIL
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.lichess.views import LichessOAuth2Adapter
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class LichessAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get("url")

    def get_avatar_url(self):
        return self.account.extra_data.get("avatar")

    def to_str(self):
        dflt = super().to_str()
        return self.account.extra_data.get("username", dflt)


class LichessProvider(OAuth2Provider):
    id = "lichess"
    name = "Lichess"
    account_class = LichessAccount
    oauth2_adapter_class = LichessOAuth2Adapter
    pkce_enabled_default = True

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        first_name = data.get("profile", {}).get("firstName")
        last_name = data.get("profile", {}).get("lastName")

        return dict(
            username=data.get("username"),
            email=data.get("email"),
            first_name=first_name,
            last_name=last_name,
        )

    def extract_email_addresses(self, data):
        ret = []
        email = data.get("email")

        if email:
            ret.append(
                EmailAddress(
                    email=email,
                    primary=True,
                )
            )
        return ret

    def get_default_scope(self):
        ret = []
        if QUERY_EMAIL:
            ret.append("email:read")
        return ret


provider_classes = [LichessProvider]
