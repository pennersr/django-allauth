from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class KakaoAccount(ProviderAccount):
    @property
    def properties(self):
        return self.account.extra_data.get("properties", {})

    @property
    def profile(self):
        return self.account.extra_data.get("kakao_account", {}).get("profile", {})

    def get_avatar_url(self):
        return self.profile.get(
            "profile_image_url", self.properties.get("profile_image")
        )

    def get_user_data(self):
        return self.account.extra_data.get("kakao_account")


class KakaoProvider(OAuth2Provider):
    id = "kakao"
    name = "Kakao"
    account_class = KakaoAccount
    oauth2_adapter_class = KakaoOAuth2Adapter

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        email = data.get("kakao_account", {}).get("email")
        nickname = data.get("kakao_account", {}).get("profile", {}).get("nickname")

        return dict(email=email, username=nickname)

    def extract_email_addresses(self, data):
        ret = []
        data = data.get("kakao_account", {})
        email = data.get("email")

        if email:
            verified = data.get("is_email_verified")
            # data['is_email_verified'] imply the email address is
            # verified
            ret.append(EmailAddress(email=email, verified=verified, primary=True))
        return ret


provider_classes = [KakaoProvider]
