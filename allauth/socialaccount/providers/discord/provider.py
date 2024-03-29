from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.discord.views import DiscordOAuth2Adapter
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class DiscordAccount(ProviderAccount):
    def validate_descriminator(self, discriminator):
        if not isinstance(discriminator, str):
            return False

        # As of 2023-06-22, Discord returns string literal '0' for users
        # with no discriminator

        return len(discriminator) == 4 if discriminator.isdigit() else False

    def is_new_username_system(self):
        if not isinstance(self.account.extra_data, dict):
            return None

        discriminator = self.account.extra_data.get("discriminator")

        if self.validate_descriminator(discriminator):
            return False

        if self.account.extra_data.get("global_name") is not None:
            return True

        return None

    def to_str(self):
        fallback = super(DiscordAccount, self).to_str()

        # If the extra_data is malformed, exit early
        if not isinstance(self.account.extra_data, dict):
            return fallback

        is_new_system = self.is_new_username_system()

        if is_new_system is None:
            # We couldn't determine if the username is new or old
            #  so we'll just return the username on it's own.
            display_name = self.account.extra_data.get("username")
        elif is_new_system:
            # global_name can be None or even undefined
            #  so we'll use the username as a fallback
            global_name = self.account.extra_data.get("global_name")
            username = self.account.extra_data.get("username")
            display_name = global_name or username
        else:
            # Looks like it's the old username system
            #  so we'll just use the username and discriminator
            display_name = "{username}#{discriminator}".format(
                username=self.account.extra_data.get("username"),
                discriminator=self.account.extra_data.get("discriminator"),
            )

        # It's very unlikely but still possible that the display_name is None
        # so we'll return or'd against the fallback just incase. We don't want
        # to return None as users of the library expect this to be str.
        return display_name or fallback

    def get_avatar_url(self):
        if (
            "id" in self.account.extra_data.keys()
            and "avatar" in self.account.extra_data.keys()
        ):
            return "https://cdn.discordapp.com/avatars/{id}/{avatar}.png".format(
                **self.account.extra_data
            )


class DiscordProvider(OAuth2Provider):
    id = "discord"
    name = "Discord"
    account_class = DiscordAccount
    oauth2_adapter_class = DiscordOAuth2Adapter

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        return dict(
            email=data.get("email"),
            username=data.get("username"),
            name=data.get("username"),
        )

    def get_default_scope(self):
        return ["email", "identify"]

    def extract_email_addresses(self, data):
        ret = []
        email = data.get("email")
        if email and data.get("verified"):
            ret.append(EmailAddress(email=email, verified=True, primary=True))
        return ret


provider_classes = [DiscordProvider]
