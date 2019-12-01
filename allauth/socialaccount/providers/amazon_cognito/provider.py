from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.amazon_cognito.utils import (
    convert_to_python_bool_if_value_is_json_string_bool,
)
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class AmazonCognitoAccount(ProviderAccount):
    def to_str(self):
        dflt = super(AmazonCognitoAccount, self).to_str()

        return self.account.extra_data.get("username", dflt)

    def get_avatar_url(self):
        return self.account.extra_data.get("picture")

    def get_profile_url(self):
        return self.account.extra_data.get("profile")


class AmazonCognitoProvider(OAuth2Provider):
    id = "amazon_cognito"
    name = "Amazon Cognito"
    account_class = AmazonCognitoAccount

    def extract_uid(self, data):
        return str(data["sub"])

    def extract_common_fields(self, data):
        return {
            "email": data.get("email"),
            "first_name": data.get("given_name"),
            "last_name": data.get("family_name"),
        }

    def get_default_scope(self):
        return ["openid", "profile", "email"]

    def extract_email_addresses(self, data):
        email = data.get("email")
        verified = convert_to_python_bool_if_value_is_json_string_bool(
            data.get("email_verified", False)
        )

        return (
            [
                EmailAddress(
                    email=email, verified=verified, primary=True
                )
            ]
            if email
            else []
        )

    def extract_extra_data(self, data):
        return {
            "address": data.get("address"),
            "birthdate": data.get("birthdate"),
            "gender": data.get("gender"),
            "locale": data.get("locale"),
            "middlename": data.get("middlename"),
            "nickname": data.get("nickname"),
            "phone_number": data.get("phone_number"),
            "phone_number_verified":
                convert_to_python_bool_if_value_is_json_string_bool(
                    data.get("phone_number_verified")
                ),
            "picture": data.get("picture"),
            "preferred_username": data.get("preferred_username"),
            "profile": data.get("profile"),
            "website": data.get("website"),
            "zoneinfo": data.get("zoneinfo"),
        }

    @classmethod
    def get_slug(cls):
        # IMPORTANT: Amazon Cognito does not support `_` characters
        #            as part of their redirect URI.
        return (
            super(AmazonCognitoProvider, cls)
            .get_slug()
            .replace("_", "-")
        )


provider_classes = [AmazonCognitoProvider]
