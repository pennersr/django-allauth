from datetime import timedelta

from django.db import models
from django.db.models import Q
from django.utils import timezone

from . import app_settings


class EmailAddressManager(models.Manager):
    def can_add_email(self, user):
        ret = True
        if app_settings.MAX_EMAIL_ADDRESSES == 1:
            # We always alow adding an email in this case, as adding
            # actually adds a temporary email that the user wants to change
            # to.
            return True
        elif app_settings.MAX_EMAIL_ADDRESSES:
            count = self.filter(user=user).count()
            ret = count < app_settings.MAX_EMAIL_ADDRESSES
        return ret

    def add_change_email(self, request, user, email):
        """
        Adds an email address the user wishes to change to, replacing his
        current email address once confirmed.
        """
        qs = self.model.objects.filter(user=user).order_by("pk")
        count = qs.count()
        instance = None
        if count > 1:
            # There are already more than 1 email addresses attached, yet,
            # there should only be 1 + a temporary one. So, try and find the best
            # temporary one to reuse.
            instance = qs.filter(verified=False, primary=False).last()
            if not instance:
                instance = qs.filter(verified=False, primary=True).last()
            if not instance:
                instance = qs.filter(verified=True, primary=False).last()
            if not instance:
                instance = qs.last()
        if not instance:
            instance = self.model.objects.create(user=user, email=email)
        else:
            # Apparently, the user was already in the process of changing his
            # email.  Reuse that temporary email address.
            instance.email = email
            instance.verified = False
            instance.primary = False
            instance.save()
        instance.send_confirmation(request)
        return instance

    def add_email(self, request, user, email, confirm=False, signup=False):
        email_address, created = self.get_or_create(
            user=user, email__iexact=email, defaults={"email": email}
        )

        if created and confirm:
            email_address.send_confirmation(request, signup=signup)

        return email_address

    def get_primary(self, user):
        try:
            return self.get(user=user, primary=True)
        except self.model.DoesNotExist:
            return None

    def get_users_for(self, email):
        # this is a list rather than a generator because we probably want to
        # do a len() on it right away
        return [
            address.user for address in self.filter(verified=True, email__iexact=email)
        ]

    def fill_cache_for_user(self, user, addresses):
        """
        In a multi-db setup, inserting records and re-reading them later
        on may result in not being able to find newly inserted
        records. Therefore, we maintain a cache for the user so that
        we can avoid database access when we need to re-read..
        """
        user._emailaddress_cache = addresses

    def get_for_user(self, user, email):
        cache_key = "_emailaddress_cache"
        addresses = getattr(user, cache_key, None)
        if addresses is None:
            ret = self.get(user=user, email__iexact=email)
            # To avoid additional lookups when e.g.
            # EmailAddress.set_as_primary() starts touching self.user
            ret.user = user
            return ret
        else:
            for address in addresses:
                if address.email.lower() == email.lower():
                    return address
            raise self.model.DoesNotExist()

    def is_verified(self, email):
        return self.filter(email__iexact=email, verified=True).exists()


class EmailConfirmationManager(models.Manager):
    def all_expired(self):
        return self.filter(self.expired_q())

    def all_valid(self):
        return self.exclude(self.expired_q())

    def expired_q(self):
        sent_threshold = timezone.now() - timedelta(
            days=app_settings.EMAIL_CONFIRMATION_EXPIRE_DAYS
        )
        return Q(sent__lt=sent_threshold)

    def delete_expired_confirmations(self):
        self.all_expired().delete()
