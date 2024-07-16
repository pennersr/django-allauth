from allauth.socialaccount.providers.amazon.views import AmazonOAuth2Adapter
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class AmazonAccount(ProviderAccount):
    pass


class AmazonProvider(OAuth2Provider):
    id = "amazon"
    name = "Amazon"
    account_class = AmazonAccount
    oauth2_adapter_class = AmazonOAuth2Adapter

    def get_default_scope(self):
        return ["profile"]

    def extract_uid(self, data):
        return str(data["user_id"])

    def extract_common_fields(self, data):
        # Hackish way of splitting the fullname.
        # Assumes no middlenames.
        name = data.get("name", "")
        first_name, last_name = name, ""
        if name and " " in name:
            first_name, last_name = name.split(" ", 1)
        return dict(
            email=data.get("email", ""), last_name=last_name, first_name=first_name
        )


provider_classes = [AmazonProvider]
