from allauth.socialaccount.providers.base import AuthAction, ProviderAccount
from allauth.socialaccount.providers.oauth.provider import OAuthProvider


class TwitterAccount(ProviderAccount):
    def get_screen_name(self):
        return self.account.extra_data.get("screen_name")

    def get_profile_url(self):
        ret = None
        screen_name = self.get_screen_name()
        if screen_name:
            ret = "http://twitter.com/" + screen_name
        return ret

    def get_avatar_url(self):
        ret = None
        profile_image_url = self.account.extra_data.get("profile_image_url")
        if profile_image_url:
            # Hmm, hack to get our hands on the large image.  Not
            # really documented, but seems to work.
            ret = profile_image_url.replace("_normal", "")
        return ret

    def to_str(self):
        screen_name = self.get_screen_name()
        return screen_name or super(TwitterAccount, self).to_str()


class TwitterProvider(OAuthProvider):
    id = "twitter"
    name = "Twitter"
    account_class = TwitterAccount

    def get_auth_url(self, request, action):
        if action == AuthAction.REAUTHENTICATE:
            url = "https://api.twitter.com/oauth/authorize"
        else:
            url = "https://api.twitter.com/oauth/authenticate"
        return url

    def extract_uid(self, data):
        return data["id"]

    def extract_common_fields(self, data):
        return dict(
            username=data.get("screen_name"),
            name=data.get("name"),
            email=data.get("email"),
        )


provider_classes = [TwitterProvider]
