import functools
from datetime import timedelta

from django.db import models
from django.db.models import Q
from django.utils import timezone

from . import app_settings


class EmailAddressManager(models.Manager):
    def can_add_email(self, user):
        ret = True
        if app_settings.CHANGE_EMAIL:
            #  We always allow adding an email in this case, regardless of
            # `MAX_EMAIL_ADDRESSES`, as adding actually adds a temporary email
            # that the user wants to change to.
            return True
        elif app_settings.MAX_EMAIL_ADDRESSES:
            count = self.filter(user=user).count()
            ret = count < app_settings.MAX_EMAIL_ADDRESSES
        return ret

    def get_new(self, user):
        """
        Returns the email address the user is in the process of changing to, if any.
        """
        assert app_settings.CHANGE_EMAIL
        return (
            self.model.objects.filter(user=user, verified=False).order_by("pk").last()
        )

    def add_new_email(self, request, user, email):
        """
        Adds an email address the user wishes to change to, replacing his
        current email address once confirmed.
        """
        assert app_settings.CHANGE_EMAIL
        instance = self.get_new(user)
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

    def get_verified(self, user):
        return self.filter(user=user, verified=True).order_by("-primary", "pk").first()

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

    def lookup(self, emails):
        q_list = [Q(email__iexact=e) for e in emails]
        if not q_list:
            return self.none()
        q = functools.reduce(lambda a, b: a | b, q_list)
        return self.filter(q)


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
