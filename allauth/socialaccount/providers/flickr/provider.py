from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.flickr.views import FlickrOAuthAdapter
from allauth.socialaccount.providers.oauth.provider import OAuthProvider


class FlickrAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get("person").get("profileurl").get("_content")

    def get_avatar_url(self):
        return self.account.extra_data.get("picture-url")

    def to_str(self):
        dflt = super(FlickrAccount, self).to_str()

        # Try to use name if it exists. If there is no name, the Flickr API
        # returns an empty string.
        name = (
            self.account.extra_data.get("person").get("realname").get("_content", None)
        )
        if name:
            return name

        # Default to username if name does not exist.
        return (
            self.account.extra_data.get("person").get("username").get("_content", dflt)
        )


class FlickrProvider(OAuthProvider):
    id = "flickr"
    name = "Flickr"
    account_class = FlickrAccount
    oauth_adapter_class = FlickrOAuthAdapter

    def get_default_scope(self):
        scope = []
        return scope

    def get_auth_params_from_request(self, request, action):
        ret = super().get_auth_params_from_request(request, action)
        if "perms" not in ret:
            ret["perms"] = "read"
        return ret

    def get_profile_fields(self):
        default_fields = [
            "id",
            "first-name",
            "last-name",
            "email-address",
            "picture-url",
            "public-profile-url",
        ]
        fields = self.get_settings().get("PROFILE_FIELDS", default_fields)
        return fields

    def extract_uid(self, data):
        return data["person"]["nsid"]

    def extract_common_fields(self, data):
        person = data.get("person", {})
        name = person.get("realname", {}).get("_content")
        username = person.get("username", {}).get("_content")
        return dict(email=data.get("email-address"), name=name, username=username)


provider_classes = [FlickrProvider]
