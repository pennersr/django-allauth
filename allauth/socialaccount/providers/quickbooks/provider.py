from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.base import ProviderAccount, ProviderException
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.quickbooks.views import QuickBooksOAuth2Adapter


class QuickBooksAccount(ProviderAccount):
    pass


class QuickBooksOAuth2Provider(OAuth2Provider):
    id = "quickbooks"
    # Name is displayed to ordinary users -- don't include protocol
    name = "QuickBooks"
    account_class = QuickBooksAccount
    oauth2_adapter_class = QuickBooksOAuth2Adapter

    def extract_uid(self, data):
        if "sub" not in data:
            raise ProviderException("QBO error", data)
        return str(data["sub"])

    def get_profile_fields(self):
        default_fields = [
            "address",
            "sub",
            "phoneNumber",
            "givenName",
            "familyName",
            "email",
            "emailVerified",
        ]
        fields = self.get_settings().get("PROFILE_FIELDS", default_fields)
        return fields

    def get_default_scope(self):
        scope = [
            "openid",
            "com.intuit.quickbooks.accounting",
            "profile",
            "phone",
        ]
        if app_settings.QUERY_EMAIL:
            scope.append("email")
        return scope

    def extract_common_fields(self, data):
        return dict(
            email=data.get("email"),
            address=data.get("address"),
            sub=data.get("sub"),
            givenName=data.get("givenName"),
            familynName=data.get("familyName"),
            emailVerified=data.get("emailVerified"),
            phoneNumber=data.get("phoneNumber"),
        )


provider_classes = [QuickBooksOAuth2Provider]
