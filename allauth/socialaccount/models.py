from django.db import models
from django.contrib.auth import authenticate
from django.contrib.auth.models import User



class SocialAccount(models.Model):
    user = models.ForeignKey(User)
    # No social_id here because I want it to be unique
    last_login = models.DateTimeField(auto_now=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def authenticate(self):
        return authenticate(account=self)


    def __unicode__(self):
        return unicode(self.user)
    
    def get_avatar_url(self):
        return None

    def get_provider(self):
        raise NotImplementedError


    def get_provider_account(self):
        for f in ['twitteraccount', 'openidaccount', 'facebookaccount']:
            if hasattr(self, f):
                try:
                    return getattr(self, f)
                except self._meta.get_field_by_name(f)[0].model.DoesNotExist:
                    pass
        assert False, "Dangling SocialAccount encountered: allauth.<foo> missing from INSTALLED_APPS ?"

    def sync(self, data):
        self.save()
