from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models, transaction
from django.db.models import Q
from django.http import HttpRequest
from django.utils import timezone

from . import app_settings


if TYPE_CHECKING:
    from .models import EmailAddress  # noqa: F401


class EmailAddressManager(models.Manager["EmailAddress"]):
    def can_add_email(self, user: AbstractBaseUser) -> bool:
        ret = True
        if app_settings.CHANGE_EMAIL:
            #  We always allow adding an email in this case, regardless of
            # `MAX_EMAIL_ADDRESSES`, as adding actually adds a temporary email
            # that the user wants to change to.
            return True
        elif app_settings.MAX_EMAIL_ADDRESSES:
            count = self.filter(user_id=user.pk).count()
            ret = count < app_settings.MAX_EMAIL_ADDRESSES
        return ret

    def get_new(self, user: AbstractBaseUser) -> EmailAddress | None:
        """
        Returns the email address the user is in the process of changing to, if any.
        """
        return self.filter(user_id=user.pk, verified=False).order_by("pk").last()

    def add_new_email(
        self,
        request: HttpRequest,
        user: AbstractBaseUser,
        email: str,
        send_verification: bool = True,
    ) -> EmailAddress:
        """
        Adds an email address the user wishes to change to, replacing his
        current email address once confirmed.
        """
        from allauth.account.internal.flows.email_verification import (
            send_verification_email_to_address,
        )

        with transaction.atomic():
            instance = self.get_new(user)
            if instance:
                instance.remove()
            email = email.lower()
            instance = self.create(
                user=user,  # type:ignore[misc]
                email=email,
            )
        if send_verification:
            send_verification_email_to_address(request, instance)
        return instance

    def add_email(
        self,
        request: HttpRequest,
        user: AbstractBaseUser,
        email,
        confirm=False,
        signup=False,
    ) -> EmailAddress:
        from allauth.account.internal.flows.email_verification import (
            send_verification_email_to_address,
        )

        email = email.lower()
        email_address, created = self.get_or_create(
            user=user, email=email, defaults={"email": email}
        )

        if created and confirm:
            send_verification_email_to_address(request, email_address)

        return email_address

    def get_verified(self, user: AbstractBaseUser) -> EmailAddress | None:
        return (
            self.filter(user_id=user.pk, verified=True)
            .order_by("-primary", "pk")
            .first()
        )

    def get_primary(self, user: AbstractBaseUser) -> EmailAddress | None:
        try:
            return self.get(user_id=user.pk, primary=True)
        except self.model.DoesNotExist:
            return None

    def get_primary_email(self, user: AbstractBaseUser) -> str | None:
        from allauth.account.utils import user_email

        primary = self.get_primary(user)
        if primary:
            email = primary.email
        else:
            email = user_email(user)
        return email

    def get_users_for(self, email) -> list[AbstractBaseUser]:
        # this is a list rather than a generator because we probably want to
        # do a len() on it right away
        return [
            address.user for address in self.filter(verified=True, email=email.lower())
        ]

    def fill_cache_for_user(self, user: AbstractBaseUser, addresses) -> None:
        """
        In a multi-db setup, inserting records and re-reading them later
        on may result in not being able to find newly inserted
        records. Therefore, we maintain a cache for the user so that
        we can avoid database access when we need to re-read..
        """
        user._emailaddress_cache = addresses  # type:ignore[attr-defined]

    def get_for_user(self, user: AbstractBaseUser, email) -> EmailAddress:
        cache_key = "_emailaddress_cache"
        addresses = getattr(user, cache_key, None)
        email = email.lower()
        if addresses is None:
            ret = self.get(user_id=user.pk, email=email.lower())
            # To avoid additional lookups when e.g.
            # EmailAddress.set_as_primary() starts touching self.user
            ret.user = user  # type:ignore[assignment]
            return ret
        else:
            for address in addresses:
                if address.email == email:
                    return address
            raise self.model.DoesNotExist()

    def is_verified(self, email: str) -> bool:
        return self.filter(email=email.lower(), verified=True).exists()

    def lookup(self, emails) -> models.QuerySet[EmailAddress]:
        return self.filter(email__in=[e.lower() for e in emails])


class EmailConfirmationManager(models.Manager):
    def all_expired(self):
        return self.filter(self.expired_q())

    def all_valid(self):
        return self.exclude(self.expired_q()).filter(email_address__verified=False)

    def expired_q(self) -> Q:
        sent_threshold = timezone.now() - timedelta(
            days=app_settings.EMAIL_CONFIRMATION_EXPIRE_DAYS
        )
        return Q(sent__lt=sent_threshold)

    def delete_expired_confirmations(self) -> None:
        self.all_expired().delete()
