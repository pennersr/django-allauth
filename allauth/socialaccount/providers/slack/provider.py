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
        team_id = data.get("https://slack.com/team_id")
        user_id = data.get("https://slack.com/user_id")
        if not (team_id and user_id):
            team_id = data.get("team").get("id")
            user_id = data.get("user").get("id")
        return "%s_%s" % (
            str(team_id),
            str(user_id),
        )

    def extract_common_fields(self, data):
        user = data.get("user", {})
        return {"name": user.get("name"), "email": user.get("email", None)}

    def get_default_scope(self):
        return ["openid", "profile", "email"]


provider_classes = [SlackProvider]
