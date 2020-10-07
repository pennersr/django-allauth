from allauth.account.models import EmailAddress
from allauth.socialaccount.app_settings import QUERY_EMAIL
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class DisqusAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get("profileUrl")

    def get_avatar_url(self):
        return self.account.extra_data.get("avatar", {}).get("permalink")

    def to_str(self):
        dflt = super(DisqusAccount, self).to_str()
        return self.account.extra_data.get("name", dflt)


class DisqusProvider(OAuth2Provider):
    id = "disqus"
    name = "Disqus"
    account_class = DisqusAccount

    def get_default_scope(self):
        scope = ["read"]
        if QUERY_EMAIL:
            scope += ["email"]
        return scope

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        return {
            "username": data.get("username"),
            "email": data.get("email"),
            "name": data.get("name"),
        }

    def extract_email_addresses(self, data):
        ret = []
        email = data.get("email")
        if email:
            ret.append(EmailAddress(email=email, verified=True, primary=True))
        return ret


provider_classes = [DisqusProvider]
