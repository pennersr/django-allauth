from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Count

from allauth.account.models import EmailAddress
from allauth.account.utils import user_email


class Command(BaseCommand):
    def handle(self, *args, **options):
        for user in self.get_users_with_multiple_primary_email():
            self.unprimary_extra_primary_emails(user)

    def get_users_with_multiple_primary_email(self):
        user_pks = []
        for email_address_dict in (
            EmailAddress.objects.filter(primary=True)
            .values("user")
            .annotate(Count("user"))
            .filter(user__count__gt=1)
        ):
            user_pks.append(email_address_dict["user"])
        return get_user_model().objects.filter(pk__in=user_pks)

    def unprimary_extra_primary_emails(self, user):
        primary_email_addresses = EmailAddress.objects.filter(user=user, primary=True)

        for primary_email_address in primary_email_addresses:
            if primary_email_address.email == user_email(user):
                break
        else:
            # Didn't find the main email addresses and break the for loop
            print(
                "WARNING: Multiple primary without a user.email match for"
                "user pk %s; (tried: %s, using: %s)"
            ) % (
                user.pk,
                ", ".join(
                    [email_address.email for email_address in primary_email_addresses]
                ),
                primary_email_address,
            )

        primary_email_addresses.exclude(pk=primary_email_address.pk).update(
            primary=False
        )
