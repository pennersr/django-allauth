from datetime import datetime

from django.db import models
from django.contrib.auth import authenticate
from django.contrib.auth.models import User



class SocialAccount(models.Model):
    user = models.ForeignKey(User)
    # No social_id here because I want it to be unique
    last_login = models.DateTimeField(default=datetime.now)
    date_joined = models.DateTimeField(default=datetime.now)

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
            try:
                return getattr(self, f)
            except self._meta.get_field_by_name(f)[0].model.DoesNotExist:
                pass
        assert False
