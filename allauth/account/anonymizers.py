from allauth.account.models import EmailAddress, EmailConfirmation
from django.utils.timezone import make_aware, utc
from anonymizer import Anonymizer
from django.conf import settings

similar_datetime = lambda anon, obj, field, val: make_aware(anon.faker.datetime(field=field, val=val), utc)
our_email = lambda anon, obj, field, val: getattr(settings, 'EMAIL_START', '') + anon.faker.name(field=field).replace(' ', '_') + getattr(settings, 'EMAIL_END', '@example.com')

class EmailAddressAnonymizer(Anonymizer):

    model = EmailAddress

    attributes = [
        ('id', "SKIP"),
        ('email', our_email),
        ('user_id', "SKIP"),
        ('verified', "SKIP"),
        ('primary', "SKIP"),
    ]


class EmailConfirmationAnonymizer(Anonymizer):

    model = EmailConfirmation

    attributes = [
        ('id', "SKIP"),
        ('key', "varchar"),
        ('email_address_id', "SKIP"),
        ('created', similar_datetime),
        ('sent', similar_datetime),
    ]
