from django.db import models, IntegrityError


class EmailAddressManager(models.Manager):
    
    def add_email(self, user, email, **kwargs):
        confirm = kwargs.pop("confirm", False)
        try:
            email_address = self.create(user=user, email=email, **kwargs)
        except IntegrityError:
            return None
        else:
            if confirm and not email_address.verified:
                email_address.send_confirmation()
            return email_address
    
    def get_primary(self, user):
        try:
            return self.get(user=user, primary=True)
        except self.model.DoesNotExist:
            return None
    
    def get_users_for(self, email):
        # this is a list rather than a generator because we probably want to
        # do a len() on it right away
        return [address.user for address in self.filter(verified=True, email=email)]


class EmailConfirmationManager(models.Manager):
    
    def delete_expired_confirmations(self):
        for confirmation in self.all():
            if confirmation.key_expired():
                confirmation.delete()
