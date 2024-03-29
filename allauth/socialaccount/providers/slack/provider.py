from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.slack.views import SlackOAuth2Adapter


class SlackAccount(ProviderAccount):
    def get_avatar_url(self):
        return self.account.extra_data.get("user").get("image_192", None)

    def to_str(self):
        dflt = super(SlackAccount, self).to_str()
        return "%s (%s)" % (
            self.account.extra_data.get("name", ""),
            dflt,
        )


class SlackProvider(OAuth2Provider):
    id = "slack"
    name = "Slack"
    account_class = SlackAccount
    oauth2_adapter_class = SlackOAuth2Adapter

    def extract_uid(self, data):
        return "%s_%s" % (
            str(data.get("team").get("id")),
            str(data.get("user").get("id")),
        )

    def extract_common_fields(self, data):
        user = data.get("user", {})
        return {"name": user.get("name"), "email": user.get("email", None)}

    def get_default_scope(self):
        return ["identify"]


provider_classes = [SlackProvider]
