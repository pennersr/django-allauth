from typing import Optional

from django.conf import settings

from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.mediawiki.views import (
    MediaWikiOAuth2Adapter,
)
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


settings = getattr(settings, "SOCIALACCOUNT_PROVIDERS", {}).get("mediawiki", {})


class MediaWikiAccount(ProviderAccount):
    def get_profile_url(self):
        userpage = settings.get(
            "USERPAGE_TEMPLATE", "https://meta.wikimedia.org/wiki/User:{username}"
        )
        username = self.account.extra_data.get("username")
        if not username:
            return None
        return userpage.format(username=username.replace(" ", "_"))

    def to_str(self):
        dflt = super(MediaWikiAccount, self).to_str()
        return self.account.extra_data.get("username", dflt)


class MediaWikiProvider(OAuth2Provider):
    id = "mediawiki"
    name = "MediaWiki"
    account_class = MediaWikiAccount
    oauth2_adapter_class = MediaWikiOAuth2Adapter

    @staticmethod
    def _get_email(data: dict) -> Optional[str]:
        if data.get("confirmed_email"):
            return data.get("email")
        return None

    def extract_uid(self, data):
        return str(data["sub"])

    def extract_extra_data(self, data):
        return dict(
            username=data.get("username"),
        )

    def extract_common_fields(self, data):
        return dict(
            email=self._get_email(data),
            username=data.get("username"),
            name=data.get("realname"),
        )

    def extract_email_addresses(self, data):
        return [EmailAddress(email=self._get_email(data), verified=True, primary=True)]


provider_classes = [MediaWikiProvider]
