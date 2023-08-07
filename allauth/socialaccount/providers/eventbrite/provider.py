"""Customise Provider classes for Eventbrite API v3."""
from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class EventbriteAccount(ProviderAccount):

    """ProviderAccount subclass for Eventbrite."""

    def get_avatar_url(self):
        """Return avatar url."""
        return self.account.extra_data["image_id"]


class EventbriteProvider(OAuth2Provider):

    """OAuth2Provider subclass for Eventbrite."""

    id = "eventbrite"
    name = "Eventbrite"
    account_class = EventbriteAccount

    def extract_uid(self, data):
        """Extract uid ('id') and ensure it's a str."""
        return str(data["id"])

    def get_default_scope(self):
        """Ensure scope is null to fit their API."""
        return [""]

    def extract_common_fields(self, data):
        """Extract fields from a basic user query."""
        email = None
        for curr_email in data.get("emails", []):
            email = email or curr_email.get("email")
            if curr_email.get("verified", False) and curr_email.get("primary", False):
                email = curr_email.get("email")

        return dict(
            email=email,
            id=data.get("id"),
            name=data.get("name"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            image_url=data.get("image_url"),
        )

    def extract_email_addresses(self, data):
        addresses = []
        for email in data.get("emails", []):
            addresses.append(
                EmailAddress(
                    email=email.get("email"),
                    verified=email.get("verfified"),
                    primary=email.get("primary"),
                )
            )

        return addresses


provider_classes = [EventbriteProvider]
