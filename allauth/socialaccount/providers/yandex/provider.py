from allauth.account.models import EmailAddress
from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.yandex.views import YandexOAuth2Adapter


class YandexAccout(ProviderAccount):
    def to_str(self):
        first_name = self.account.extra_data.get("first_name", "")
        last_name = self.account.extra_data.get("last_name", "")
        name = " ".join([first_name, last_name]).strip()
        return name or super(YandexAccout, self).to_str()


class YandexProvider(OAuth2Provider):
    id = "yandex"
    name = "Yandex"
    account_class = YandexAccout
    oauth2_adapter_class = YandexOAuth2Adapter

    def get_default_scope(self):
        scope = ["login:info"]
        if app_settings.QUERY_EMAIL:
            scope.append("login:email")
        return scope

    def extract_uid(self, data):
        return str(data["id"])

    def get_user_email(self, data):
        email = data.get("default_email")
        if not email:
            emails = data.get("emails")
            email = emails[0] if emails else ""
        return email

    def extract_common_fields(self, data):
        email = self.get_user_email(data)
        return dict(
            email=email,
            last_name=data.get("last_name"),
            username=data.get("display_name"),
            first_name=data.get("first_name"),
        )

    def extract_email_addresses(self, data):
        ret = []
        email = self.get_user_email(data)
        if email:
            ret.append(EmailAddress(email=email, verified=True, primary=True))
        return ret


provider_classes = [YandexProvider]
