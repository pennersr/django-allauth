from django.utils import simplejson

from allauth.socialaccount.oauth import OAuth

class OAuthTwitter(OAuth):
    """
    Verifying twitter credentials
    """
    url = 'https://twitter.com/account/verify_credentials.json'

    def get_user_info(self):
        user = simplejson.loads(self.query(self.url))
        return user
