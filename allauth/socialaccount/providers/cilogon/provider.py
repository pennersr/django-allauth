from allauth.account.models import EmailAddress
from allauth.socialaccount.app_settings import QUERY_EMAIL
from allauth.socialaccount.providers.base import AuthAction, ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class Scope(object):
    OPENID = "openid"
    EMAIL = "email"
    PROFILE = "profile"
    USERINFO = "org.cilogon.userinfo"


class CILogonAccount(ProviderAccount):
    def to_str(self):
        dflt = super(CILogonAccount, self).to_str()
        return self.account.extra_data.get("name", dflt)


class CILogonProvider(OAuth2Provider):
    id = "cilogon"
    name = "CILogon"
    account_class = CILogonAccount

    def get_default_scope(self):
        scope = [Scope.PROFILE, Scope.USERINFO, Scope.OPENID]
        if QUERY_EMAIL:
            scope.append(Scope.EMAIL)
        return scope

    def get_auth_params(self, request, action):
        ret = super(CILogonProvider, self).get_auth_params(request, action)
        if action == AuthAction.REAUTHENTICATE:
            ret["prompt"] = "select_account consent"
        return ret

    def extract_uid(self, data):
        return str(data.get("sub"))

    def extract_common_fields(self, data):
        return dict(
            email=data.get("email"),
            last_name=data.get("family_name"),
            first_name=data.get("given_name"),
            eppn=data.get("eppn"),
        )

    def extract_email_addresses(self, data):
        ret = []
        email = data.get("email")
        if email and data.get("verified_email"):
            ret.append(EmailAddress(email=email, verified=True, primary=True))
        return ret


provider_classes = [CILogonProvider]
