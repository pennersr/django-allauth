from allauth.socialaccount.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.yahoo.views import YahooOAuth2Adapter


class YahooAccount(ProviderAccount):
    def to_str(self):
        name = "{0} {1}".format(
            self.account.extra_data.get("given_name", ""),
            self.account.extra_data.get("family_name", ""),
        )
        if name.strip() != "":
            return name
        return super(YahooAccount, self).to_str()


class YahooProvider(OAuth2Provider):
    id = str("yahoo")
    name = "Yahoo"
    account_class = YahooAccount
    oauth2_adapter_class = YahooOAuth2Adapter

    def get_default_scope(self):
        """
        Doc on scopes available at
        https://developer.yahoo.com/oauth2/guide/yahoo_scopes/
        """
        return ["profile", "email"]

    def extract_uid(self, data):
        return data["sub"]

    def extract_common_fields(self, data):
        return dict(
            email=data["email"],
            last_name=data["family_name"],
            first_name=data["given_name"],
        )

    def extract_email_addresses(self, data):
        ret = []
        email = data.get("email")
        if email and data.get("email_verified"):
            ret.append(EmailAddress(email=email, verified=True, primary=True))
        return ret


provider_classes = [YahooProvider]
