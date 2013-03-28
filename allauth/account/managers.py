from datetime import timedelta

from django.utils import timezone
from django.db import models, IntegrityError
from django.db.models import Q

from . import app_settings

class EmailAddressManager(models.Manager):
    
    def add_email(self, request, user, email, **kwargs):
        confirm = kwargs.pop("confirm", False)
        try:
            email_address = self.create(user=user, email=email, **kwargs)
        except IntegrityError:
            return None
        else:
            if confirm and not email_address.verified:
                email_address.send_confirmation(request)
            return email_address
    
    def get_primary(self, user):
        try:
            return self.get(user=user, primary=True)
        except self.model.DoesNotExist:
            return None
    
    def get_users_for(self, email):
        # this is a list rather than a generator because we probably want to
        # do a len() on it right away
        return [address.user for address in self.filter(verified=True, 
                                                        email=email)]


class EmailConfirmationManager(models.Manager):

    def all_expired(self):
        return self.filter(self.expired_q())

    def all_valid(self):
        return self.exclude(self.expired_q())

    def expired_q(self):
        sent_threshold = timezone.now() \
            - timedelta(days=app_settings.EMAIL_CONFIRMATION_EXPIRE_DAYS)
        return Q(sent__lt=sent_threshold)
    
    def delete_expired_confirmations(self):
        self.all_expired().delete()
