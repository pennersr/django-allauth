from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth.provider import OAuthProvider

class TwitterAccount(ProviderAccount):
    def get_screen_name(self):
        return self.account.extra_data.get('screen_name')

    def get_profile_url(self):
        ret = None
        screen_name = self.get_screen_name()
        if screen_name:
            ret = 'http://twitter.com/' + screen_name
        return ret

    def get_avatar_url(self):
        ret = None
        profile_image_url = self.account.extra_data.get('profile_image_url')
        if profile_image_url:
            # Hmm, hack to get our hands on the large image.  Not
            # really documented, but seems to work.
            ret = profile_image_url.replace('_normal', '')
        return ret

    def to_str(self):
        screen_name = self.get_screen_name()
        return screen_name or super(TwitterAccount, self).to_str()


class TwitterProvider(OAuthProvider):
    id = 'twitter'
    name = 'Twitter'
    package = 'allauth.socialaccount.providers.twitter'
    account_class = TwitterAccount
        
        
providers.registry.register(TwitterProvider)
