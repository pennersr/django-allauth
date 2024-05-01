from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.odnoklassniki.views import (
    OdnoklassnikiOAuth2Adapter,
)


class OdnoklassnikiAccount(ProviderAccount):
    def get_profile_url(self):
        return "https://ok.ru/profile/" + self.account.extra_data["uid"]

    def get_avatar_url(self):
        ret = None
        pic_big_url = self.account.extra_data.get("pic1024x768")
        pic_medium_url = self.account.extra_data.get("pic640x480")
        pic_small_url = self.account.extra_data.get("pic190x190")
        if pic_big_url:
            return pic_big_url
        elif pic_medium_url:
            return pic_medium_url
        elif pic_small_url:
            return pic_small_url
        else:
            return ret

    def to_str(self):
        dflt = super(OdnoklassnikiAccount, self).to_str()
        return self.account.extra_data.get("name", dflt)


class OdnoklassnikiProvider(OAuth2Provider):
    id = "odnoklassniki"
    name = "Odnoklassniki"
    account_class = OdnoklassnikiAccount
    oauth2_adapter_class = OdnoklassnikiOAuth2Adapter

    def extract_uid(self, data):
        return data["uid"]

    def extract_common_fields(self, data):
        return dict(
            last_name=data.get("last_name"),
            first_name=data.get("first_name"),
            email=data.get("email"),
        )


provider_classes = [OdnoklassnikiProvider]
