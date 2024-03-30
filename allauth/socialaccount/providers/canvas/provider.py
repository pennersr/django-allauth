from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.canvas.views import (
    CanvasOAuth2Adapter,
)
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.account.models import EmailAddress


class CanvasAccount(ProviderAccount):
    def get_avatar_url(self):
        return self.account.extra_data.get("avatar_url", "")

    def to_str(self):
        name = super(CanvasAccount, self).to_str()
        return self.account.extra_data.get("name", name)


class CanvasProvider(OAuth2Provider):
    id = "canvas"
    name = "Canvas"
    account_class = CanvasAccount
    oauth2_adapter_class = CanvasOAuth2Adapter

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        return {
            "username": data.get("login_id"),
            "email": data.get("primary_email"),
            "name": data.get("name"),
        }

    def extract_email_addresses(self, data):
        ret = []
        email = data.get("primary_email")
        if email:
            ret.append(EmailAddress(email=email, verified=True, primary=True))
        return ret

    def get_default_scope(self):
        scope = []
        return scope


provider_classes = [CanvasProvider]
