from django.conf import settings
from django.db import migrations
from django.db.models import Count


def forwards(apps, schema_editor):
    EmailAddress = apps.get_model("account.EmailAddress")
    User = apps.get_model(settings.AUTH_USER_MODEL)
    user_email_field = getattr(settings, "ACCOUNT_USER_MODEL_EMAIL_FIELD", "email")

    def get_users_with_multiple_primary_email():
        user_pks = []
        for email_address_dict in (
            EmailAddress.objects.filter(primary=True)
            .values("user")
            .annotate(Count("user"))
            .filter(user__count__gt=1)
        ):
            user_pks.append(email_address_dict["user"])
        return User.objects.filter(pk__in=user_pks)

    def unset_extra_primary_emails(user):
        qs = EmailAddress.objects.filter(user=user, primary=True)
        primary_email_addresses = list(qs)
        if not primary_email_addresses:
            return
        primary_email_address = primary_email_addresses[0]
        if user_email_field:
            for address in primary_email_addresses:
                if address.email.lower() == getattr(user, user_email_field, "").lower():
                    primary_email_address = address
                    break
        qs.exclude(pk=primary_email_address.pk).update(primary=False)

    for user in get_users_with_multiple_primary_email().iterator(2000):
        unset_extra_primary_emails(user)


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0007_emailaddress_idx_email"),
    ]

    operations = [
        migrations.RunPython(code=forwards, reverse_code=migrations.RunPython.noop)
    ]
