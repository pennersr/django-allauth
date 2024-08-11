from allauth.account.models import EmailAddress
from allauth.socialaccount.app_settings import QUERY_EMAIL
from allauth.socialaccount.providers.base import AuthAction, ProviderAccount
from allauth.socialaccount.providers.cilogon.views import CILogonOAuth2Adapter
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class Scope:
    OPENID = "openid"
    EMAIL = "email"
    PROFILE = "profile"
    USERINFO = "org.cilogon.userinfo"


class CILogonAccount(ProviderAccount):
    pass


class CILogonProvider(OAuth2Provider):
    id = "cilogon"
    name = "CILogon"
    account_class = CILogonAccount
    oauth2_adapter_class = CILogonOAuth2Adapter

    def get_default_scope(self):
        scope = [Scope.PROFILE, Scope.USERINFO, Scope.OPENID]
        if QUERY_EMAIL:
            scope.append(Scope.EMAIL)
        return scope

    def get_auth_params_from_request(self, request, action):
        ret = super().get_auth_params_from_request(request, action)
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
