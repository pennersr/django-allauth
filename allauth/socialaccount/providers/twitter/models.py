from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import Provider, ProviderAccount

class TwitterAccount(ProviderAccount):
    def get_profile_url(self):
        ret = None
        screen_name = self.account.extra_data.get('screen_name')
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


class TwitterProvider(Provider):
    id = 'twitter'
    package = 'allauth.socialaccount.providers.twitter'
    account_class = TwitterAccount

providers.registry.register_provider(TwitterProvider)
